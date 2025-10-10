import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
import json
import uuid
import logging
import time

# Import our custom modules
from auth import (
    require_admin_login, show_admin_management, get_current_admin, get_current_user_info,
    is_admin_logged_in, is_user_logged_in, show_login_page, get_current_user
)
from scheduler_manager import schedule_reminder, cancel_reminder, get_scheduled_jobs, reschedule_all_reminders

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Reminder System",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication - allow both admin and user access
if not is_admin_logged_in() and not is_user_logged_in():
    show_login_page()
    st.stop()

# Constants
EXCEL_FILE = "payment_reminders.xlsx"
CONFIG_FILE = "email_config.json"

# Initialize session state
if 'reminders_df' not in st.session_state:
    st.session_state.reminders_df = pd.DataFrame()
if 'email_config' not in st.session_state:
    st.session_state.email_config = {}
if 'selected_reminders' not in st.session_state:
    st.session_state.selected_reminders = []
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edit_reminder_id' not in st.session_state:
    st.session_state.edit_reminder_id = None
if 'scheduler_initialized' not in st.session_state:
    st.session_state.scheduler_initialized = False
    # Initialize scheduler and reschedule existing reminders
    reschedule_all_reminders()
    st.session_state.scheduler_initialized = True

def load_email_config():
    """Load email configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_email_config(config):
    """Save email configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_reminders():
    """Load reminders from Excel file"""
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE, sheet_name="Reminders")
            # Add ID column if it doesn't exist
            if 'ID' not in df.columns:
                df['ID'] = [str(uuid.uuid4()) for _ in range(len(df))]
                save_reminders(df)
            return df
        else:
            # Create empty DataFrame with required columns
            columns = ['ID', 'Name', 'Email', 'Header Name', 'Due Date', 'Due Time', 'Message', 'Status', 'Last Sent']
            return pd.DataFrame(columns=columns)
    except Exception as e:
        st.error(f"Error loading reminders: {str(e)}")
        return pd.DataFrame()

def save_reminders(df):
    """Save reminders to Excel file"""
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Reminders", index=False)
        return True
    except Exception as e:
        st.error(f"Error saving reminders: {str(e)}")
        return False

def send_email(recipient, subject, body, sender_email=None, app_password=None):
    """Send email reminder using configured email accounts"""
    try:
        # If no sender specified, use default from admin management
        if not sender_email or not app_password:
            from auth import get_default_email_account
            default_account = get_default_email_account()

            if not default_account:
                st.error("No email account configured in admin management")
                return False

            sender_email = default_account["email"]
            app_password = default_account["password"]

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient, msg.as_string())

        # Update email usage statistics
        try:
            from auth import load_email_accounts, save_email_accounts
            accounts = load_email_accounts()
            if sender_email in accounts:
                accounts[sender_email]["total_sent"] = accounts[sender_email].get("total_sent", 0) + 1
                accounts[sender_email]["last_used"] = datetime.now().isoformat()
                save_email_accounts(accounts)
        except:
            pass  # Don't fail email sending if stats update fails

        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

def check_and_send_reminders():
    """Check for due reminders and send them"""
    # Check if email accounts are configured in admin management
    try:
        import base64
        from auth import get_default_email_account
        default_account = get_default_email_account()
        if not default_account:
            return "No email account configured in Admin Management"

        sender_email = default_account["email"]
        app_password = default_account["password"]

        # The password from admin management is base64 encoded, decode it
        try:
            decoded_password = base64.b64decode(app_password).decode('utf-8')
            app_password = decoded_password
        except:
            # If decoding fails, use the password as-is
            pass

    except Exception as e:
        # Fallback to old config system
        config = load_email_config()
        if not config.get('sender_email') or not config.get('app_password'):
            return f"Email configuration not set: {str(e)}"
        sender_email = config['sender_email']
        app_password = config['app_password']

    df = load_reminders()
    if df.empty:
        return "No reminders found"

    today = datetime.today().date()
    current_time = datetime.now().time()
    sent_count = 0

    for index, row in df.iterrows():
        if pd.notna(row['Due Date']):
            due_date = pd.to_datetime(row['Due Date']).date()
            due_time = pd.to_datetime(row.get('Due Time', '09:00')).time() if pd.notna(row.get('Due Time')) else datetime.strptime('09:00', '%H:%M').time()

            if due_date == today and current_time >= due_time and row.get('Status', 'Active') == 'Active':
                try:
                    # Safely get header name with fallback for old data
                    header_name = row.get('Header Name', row.get('Agreement Name', 'Reminder'))

                    subject = f"Reminder - {header_name}"
                    body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"

                    if send_email(row['Email'], subject, body, sender_email, app_password):
                        df.at[index, 'Last Sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        sent_count += 1
                except Exception as e:
                    logger.error(f"Error processing reminder {row.get('ID', 'unknown')}: {str(e)}")

    if sent_count > 0:
        save_reminders(df)

    return f"Sent {sent_count} reminders"

def send_selected_reminders(selected_ids):
    """Send reminders to selected recipients"""
    # Check if email accounts are configured in admin management
    try:
        import base64
        from auth import get_default_email_account
        default_account = get_default_email_account()
        if not default_account:
            return "No email account configured in Admin Management"

        sender_email = default_account["email"]
        app_password = default_account["password"]

        # The password from admin management is base64 encoded, decode it
        try:
            decoded_password = base64.b64decode(app_password).decode('utf-8')
            app_password = decoded_password
        except:
            # If decoding fails, use the password as-is
            pass

    except Exception as e:
        # Fallback to old config system
        config = load_email_config()
        if not config.get('sender_email') or not config.get('app_password'):
            return f"Email configuration not set: {str(e)}"
        sender_email = config['sender_email']
        app_password = config['app_password']

    df = load_reminders()
    if df.empty:
        return "No reminders found"

    sent_count = 0
    failed_count = 0

    for reminder_id in selected_ids:
        row = df[df['ID'] == reminder_id].iloc[0] if not df[df['ID'] == reminder_id].empty else None
        if row is not None:
            try:
                # Safely get header name with fallback for old data
                header_name = row.get('Header Name', row.get('Agreement Name', 'Reminder'))

                subject = f"Reminder - {header_name}"
                body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"

                if send_email(row['Email'], subject, body, sender_email, app_password):
                    df.loc[df['ID'] == reminder_id, 'Last Sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error processing reminder {reminder_id}: {str(e)}")
                failed_count += 1

    if sent_count > 0:
        save_reminders(df)

    return f"Sent {sent_count} reminders, {failed_count} failed"

def delete_selected_reminders(selected_ids):
    """Delete selected reminders"""
    df = load_reminders()
    if df.empty:
        return "No reminders found"

    initial_count = len(df)

    # Cancel scheduled jobs for deleted reminders
    for reminder_id in selected_ids:
        cancel_reminder(reminder_id)
        logger.info(f"Cancelled scheduled job for deleted reminder {reminder_id}")

    df = df[~df['ID'].isin(selected_ids)]
    deleted_count = initial_count - len(df)

    if deleted_count > 0:
        save_reminders(df)
        st.session_state.reminders_df = df

    return f"Deleted {deleted_count} reminders"

def update_reminder(reminder_id, updated_data):
    """Update a specific reminder"""
    df = load_reminders()
    if df.empty or reminder_id not in df['ID'].values:
        return False

    # Get old data for comparison
    old_row = df[df['ID'] == reminder_id].iloc[0]
    old_due_date = old_row['Due Date']
    old_due_time = old_row.get('Due Time', '09:00')
    old_status = old_row.get('Status', 'Active')

    # Update the data
    for key, value in updated_data.items():
        df.loc[df['ID'] == reminder_id, key] = value

    if save_reminders(df):
        st.session_state.reminders_df = df

        # Handle rescheduling if date, time, or status changed
        new_due_date = updated_data.get('Due Date', old_due_date)
        new_due_time = updated_data.get('Due Time', old_due_time)
        new_status = updated_data.get('Status', old_status)

        # Cancel existing scheduled job
        cancel_reminder(reminder_id)

        # Reschedule if active and in the future
        if new_status == 'Active':
            if isinstance(new_due_date, str):
                new_due_date = datetime.strptime(new_due_date, '%Y-%m-%d').date()

            scheduled_datetime = datetime.combine(new_due_date, datetime.strptime(new_due_time, '%H:%M').time())
            if scheduled_datetime > datetime.now():
                schedule_reminder(reminder_id, new_due_date, new_due_time)
                logger.info(f"Rescheduled reminder {reminder_id} for {scheduled_datetime}")

        return True
    return False

# Sidebar navigation
st.sidebar.title("📧 Reminder System")

# Show user info
if is_admin_logged_in():
    current_user = get_current_admin()
    user_type = "👑 Admin"
    st.sidebar.success(f"{user_type}: {current_user}")
elif is_user_logged_in():
    current_user = get_current_user()
    user_type = "👤 User"
    st.sidebar.info(f"{user_type}: {current_user}")

# Handle edit mode navigation
if st.session_state.edit_mode and st.session_state.edit_reminder_id:
    page = "✏️ Edit Reminder"
    st.sidebar.info("📝 Currently editing a reminder")
    if st.sidebar.button("❌ Cancel Edit"):
        st.session_state.edit_mode = False
        st.session_state.edit_reminder_id = None
        st.rerun()
else:
    # Initialize page in session state if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Dashboard"

    # Different navigation options based on user type
    if is_admin_logged_in():
        # Full admin navigation
        page = st.sidebar.selectbox("Navigate", [
            "🏠 Dashboard",
            "➕ Add Reminder",
            "📋 Manage Reminders",
            "🎯 Selective Mailing",
            "⚙️ Email Settings",
            "📤 Send Now",
            "🔧 Scheduler Status",
            "👥 Admin Management"
        ])
    else:
        # Limited user navigation
        page = st.sidebar.selectbox("Navigate", [
            "🏠 Dashboard",
            "➕ Add Reminder",
            "📋 Manage Reminders",
            "🎯 Selective Mailing",
            "📤 Send Now",
            "🔧 Scheduler Status"
        ])

    # Update session state with selected page
    st.session_state.page = page

# Load data
st.session_state.reminders_df = load_reminders()
st.session_state.email_config = load_email_config()

# Main content based on selected page
if page == "🏠 Dashboard":
    st.title("🏠 Enhanced Reminder Dashboard")

    # Get current user info
    user_info = get_current_user_info()
    admin_email = get_current_admin()

    # Welcome section with enhanced info
    col_welcome1, col_welcome2 = st.columns([2, 1])
    with col_welcome1:
        role = user_info.get('role', 'admin')
        role_display = "Primary Administrator" if role == "primary_admin" else "Administrator"
        st.markdown(f"### Welcome back, **{role_display}**! 👋")
        st.markdown(f"**Email:** {admin_email}")

    with col_welcome2:
        # Show permissions
        permissions = user_info.get('permissions', {})
        st.markdown("**Your Access Level:**")
        if permissions.get('system_admin'):
            st.success("🔧 System Administrator")
        elif permissions.get('manage_users'):
            st.info("👥 User Manager")
        else:
            st.info("📧 Standard Admin")

    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)

    df = st.session_state.reminders_df

    with col1:
        st.metric("📧 Total Reminders", len(df))

    with col2:
        active_count = len(df[df.get('Status', 'Active') == 'Active']) if not df.empty else 0
        st.metric("✅ Active", active_count)

    with col3:
        today = datetime.today().date()
        if not df.empty and 'Due Date' in df.columns:
            due_today = len(df[pd.to_datetime(df['Due Date'], errors='coerce').dt.date == today])
        else:
            due_today = 0
        st.metric("📅 Due Today", due_today)

    with col4:
        # Next 7 days
        if not df.empty and 'Due Date' in df.columns:
            next_week = today + timedelta(days=7)
            upcoming = len(df[
                (pd.to_datetime(df['Due Date'], errors='coerce').dt.date >= today) &
                (pd.to_datetime(df['Due Date'], errors='coerce').dt.date <= next_week)
            ])
        else:
            upcoming = 0
        st.metric("📆 This Week", upcoming)

    with col5:
        # Get scheduled jobs count
        jobs = get_scheduled_jobs()
        st.metric("⏰ Scheduled", len(jobs))

    # System status indicators
    st.subheader("🔧 System Status")
    col_status1, col_status2, col_status3, col_status4 = st.columns(4)

    with col_status1:
        st.success("✅ Authentication Active")
    with col_status2:
        st.success("✅ Scheduler Running")
    with col_status3:
        if os.path.exists("email_config.json"):
            st.success("✅ Email Configured")
        else:
            st.warning("⚠️ Email Setup Needed")
    with col_status4:
        if len(jobs) > 0:
            st.info(f"⏰ {len(jobs)} Jobs Queued")
        else:
            st.info("⏰ No Jobs Scheduled")

    # Recent activity
    st.subheader("📅 Upcoming Reminders")
    if not df.empty and 'Due Date' in df.columns:
        upcoming_df = df[pd.to_datetime(df['Due Date'], errors='coerce').dt.date >= today].copy()
        if not upcoming_df.empty:
            upcoming_df['Due Date'] = pd.to_datetime(upcoming_df['Due Date'])
            upcoming_df = upcoming_df.sort_values('Due Date').head(10)
            st.dataframe(upcoming_df[['Name', 'Header Name', 'Due Date', 'Email']], use_container_width=True)
        else:
            st.info("No upcoming reminders")
    else:
        st.info("No reminders configured yet")

    # Quick actions based on permissions
    st.subheader("⚡ Quick Actions")
    if user_info.get('permissions', {}).get('manage_users'):
        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
        with col_action4:
            if st.button("👥 Admin Management", type="secondary"):
                # Navigate to admin management (will be handled by sidebar)
                pass
    else:
        col_action1, col_action2, col_action3 = st.columns(3)

    with col_action1:
        if st.button("➕ Add New Reminder", type="primary"):
            pass  # Navigation handled by sidebar

    with col_action2:
        if st.button("📋 Manage Reminders"):
            pass  # Navigation handled by sidebar

    with col_action3:
        if st.button("🎯 Selective Mailing"):
            pass  # Navigation handled by sidebar

elif page == "➕ Add Reminder":
    st.title("➕ Add New Reminder")

    with st.form("add_reminder_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Contact Name*", placeholder="John Doe")
            email = st.text_input("Email Address*", placeholder="john@example.com")
            header_name = st.text_input("Header Name*", placeholder="Monthly Rent Payment")

        with col2:
            due_date = st.date_input("Due Date*", value=datetime.today().date())
            due_time = st.time_input("Due Time*", value=datetime.strptime("09:00", "%H:%M").time())
            status = st.selectbox("Status", ["Active", "Inactive"], index=0)

        message = st.text_area(
            "Reminder Message*",
            placeholder="This is a friendly reminder that your payment is due today...",
            height=100
        )

        # Auto-scheduling option
        auto_schedule = st.checkbox("📅 Auto-schedule this reminder", value=True,
                                   help="Automatically send email at the specified date and time")

        submitted = st.form_submit_button("Add Reminder", type="primary")

        if submitted:
            if name and email and header_name and message:
                reminder_id = str(uuid.uuid4())
                new_reminder = {
                    'ID': reminder_id,
                    'Name': name,
                    'Email': email,
                    'Header Name': header_name,
                    'Due Date': due_date,
                    'Due Time': due_time.strftime('%H:%M'),
                    'Message': message,
                    'Status': status,
                    'Last Sent': ''
                }

                df = st.session_state.reminders_df
                new_df = pd.concat([df, pd.DataFrame([new_reminder])], ignore_index=True)

                if save_reminders(new_df):
                    st.success("✅ Reminder added successfully!")

                    # Schedule the reminder if auto-schedule is enabled
                    if auto_schedule and status == 'Active':
                        scheduled_datetime = datetime.combine(due_date, due_time)
                        if scheduled_datetime > datetime.now():
                            if schedule_reminder(reminder_id, due_date, due_time.strftime('%H:%M')):
                                st.success(f"📅 Reminder scheduled for {due_date} at {due_time}")
                                logger.info(f"Scheduled reminder {reminder_id} for {scheduled_datetime}")
                            else:
                                st.warning("⚠️ Reminder saved but scheduling failed. Check scheduler logs.")
                        else:
                            st.warning("⚠️ Scheduled time is in the past. Reminder saved but not scheduled.")

                    st.session_state.reminders_df = new_df
                    st.rerun()
                else:
                    st.error("❌ Failed to save reminder")
            else:
                st.error("❌ Please fill in all required fields")

elif page == "📋 Manage Reminders":
    st.title("📋 Manage Payment Reminders")

    df = st.session_state.reminders_df

    if not df.empty:
        # Search and filter controls
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search reminders", placeholder="Search by name, email, or agreement...")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col3:
            date_filter = st.selectbox("Filter by Date", ["All", "Due Today", "Due This Week", "Overdue"])
        with col4:
            if st.button("🔄 Refresh"):
                st.rerun()

        # Apply filters
        filtered_df = df.copy()

        # Text search filter
        if search_term:
            mask = (
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['Email'].str.contains(search_term, case=False, na=False) |
                filtered_df['Header Name'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]

        # Status filter
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df.get('Status', 'Active') == status_filter]

        # Date filter
        if date_filter != "All":
            today = datetime.today().date()
            if date_filter == "Due Today":
                filtered_df = filtered_df[pd.to_datetime(filtered_df['Due Date'], errors='coerce').dt.date == today]
            elif date_filter == "Due This Week":
                week_end = today + timedelta(days=7)
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df['Due Date'], errors='coerce').dt.date >= today) &
                    (pd.to_datetime(filtered_df['Due Date'], errors='coerce').dt.date <= week_end)
                ]
            elif date_filter == "Overdue":
                filtered_df = filtered_df[pd.to_datetime(filtered_df['Due Date'], errors='coerce').dt.date < today]

        # Display reminders with selection
        if not filtered_df.empty:
            st.subheader(f"📊 Found {len(filtered_df)} reminders")

            # Selection controls
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                select_all = st.checkbox("Select All")
            with col2:
                if st.button("Clear Selection"):
                    st.session_state.selected_reminders = []
                    st.rerun()

            # Handle select all
            if select_all:
                st.session_state.selected_reminders = filtered_df['ID'].tolist()

            # Display table with checkboxes
            display_df = filtered_df.copy()

            # Create selection column
            selected_items = []
            for idx, row in display_df.iterrows():
                is_selected = row['ID'] in st.session_state.selected_reminders
                selected_items.append(is_selected)

            # Show data with edit buttons
            for idx, row in display_df.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 2, 2, 1.5, 1])

                    with col1:
                        is_selected = st.checkbox("", key=f"select_{row['ID']}",
                                                value=row['ID'] in st.session_state.selected_reminders)
                        if is_selected and row['ID'] not in st.session_state.selected_reminders:
                            st.session_state.selected_reminders.append(row['ID'])
                        elif not is_selected and row['ID'] in st.session_state.selected_reminders:
                            st.session_state.selected_reminders.remove(row['ID'])

                    with col2:
                        st.write(f"**{row['Name']}**")
                        st.write(f"📧 {row['Email']}")

                    with col3:
                        st.write(f"📋 {row['Header Name']}")
                        st.write(f"📅 {row['Due Date']} at {row.get('Due Time', '09:00')}")

                    with col4:
                        st.write(f"🔄 {row.get('Status', 'Active')}")
                        if row.get('Last Sent'):
                            st.write(f"📤 Last sent: {row['Last Sent']}")
                        else:
                            st.write("📤 Never sent")

                    with col5:
                        if st.button("✏️ Edit", key=f"edit_{row['ID']}"):
                            st.session_state.edit_mode = True
                            st.session_state.edit_reminder_id = row['ID']
                            st.rerun()

                    with col6:
                        if st.button("🗑️", key=f"delete_{row['ID']}", help="Delete this reminder"):
                            if delete_selected_reminders([row['ID']]):
                                st.success("✅ Reminder deleted!")
                                st.rerun()

                    st.divider()

            # Bulk actions
            if st.session_state.selected_reminders:
                st.subheader(f"🎯 Bulk Actions ({len(st.session_state.selected_reminders)} selected)")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button("📧 Send Selected", type="primary"):
                        result = send_selected_reminders(st.session_state.selected_reminders)
                        st.success(f"✅ {result}")
                        st.session_state.selected_reminders = []
                        st.rerun()

                with col2:
                    if st.button("🗑️ Delete Selected", type="secondary"):
                        if st.session_state.get('confirm_bulk_delete', False):
                            result = delete_selected_reminders(st.session_state.selected_reminders)
                            st.success(f"✅ {result}")
                            st.session_state.selected_reminders = []
                            st.session_state.confirm_bulk_delete = False
                            st.rerun()
                        else:
                            st.session_state.confirm_bulk_delete = True
                            st.warning("⚠️ Click again to confirm deletion")

                with col3:
                    if st.button("✅ Activate Selected"):
                        df_updated = load_reminders()
                        df_updated.loc[df_updated['ID'].isin(st.session_state.selected_reminders), 'Status'] = 'Active'
                        save_reminders(df_updated)
                        st.success("✅ Selected reminders activated!")
                        st.session_state.selected_reminders = []
                        st.rerun()

                with col4:
                    if st.button("❌ Deactivate Selected"):
                        df_updated = load_reminders()
                        df_updated.loc[df_updated['ID'].isin(st.session_state.selected_reminders), 'Status'] = 'Inactive'
                        save_reminders(df_updated)
                        st.success("✅ Selected reminders deactivated!")
                        st.session_state.selected_reminders = []
                        st.rerun()
        else:
            st.info("No reminders match your search criteria")
    else:
        st.info("No reminders found. Add your first reminder using the 'Add Reminder' page.")

elif page == "✏️ Edit Reminder":
    st.title("✏️ Edit Payment Reminder")

    if not st.session_state.edit_mode or not st.session_state.edit_reminder_id:
        st.warning("⚠️ No reminder selected for editing. Please go to 'Manage Reminders' and select a reminder to edit.")
        if st.button("📋 Go to Manage Reminders"):
            # Reset to manage reminders by clearing edit mode
            st.session_state.edit_mode = False
            st.session_state.edit_reminder_id = None
            st.rerun()
    else:
        df = load_reminders()
        reminder_row = df[df['ID'] == st.session_state.edit_reminder_id]

        if reminder_row.empty:
            st.error("❌ Reminder not found!")
            st.session_state.edit_mode = False
            st.session_state.edit_reminder_id = None
        else:
            reminder = reminder_row.iloc[0]

            st.info(f"📝 Editing reminder for: **{reminder['Name']}** - **{reminder['Header Name']}**")

            with st.form("edit_reminder_form"):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Contact Name*", value=reminder['Name'])
                    email = st.text_input("Email Address*", value=reminder['Email'])
                    header_name = st.text_input("Header Name*", value=reminder['Header Name'])

                with col2:
                    due_date = st.date_input("Due Date*", value=pd.to_datetime(reminder['Due Date']).date())
                    due_time_str = reminder.get('Due Time', '09:00')
                    due_time = st.time_input("Due Time*", value=datetime.strptime(due_time_str, '%H:%M').time())
                    status = st.selectbox("Status", ["Active", "Inactive"],
                                        index=0 if reminder.get('Status', 'Active') == 'Active' else 1)

                message = st.text_area(
                    "Reminder Message*",
                    value=reminder['Message'],
                    height=100
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    update_submitted = st.form_submit_button("💾 Update Reminder", type="primary")

                with col2:
                    cancel_submitted = st.form_submit_button("❌ Cancel")

                with col3:
                    delete_submitted = st.form_submit_button("🗑️ Delete", type="secondary")

                # Handle form submissions outside the form
                if cancel_submitted:
                    st.session_state.edit_mode = False
                    st.session_state.edit_reminder_id = None
                    st.rerun()

                if delete_submitted:
                    if delete_selected_reminders([st.session_state.edit_reminder_id]):
                        st.success("✅ Reminder deleted!")
                        st.session_state.edit_mode = False
                        st.session_state.edit_reminder_id = None
                        st.rerun()

                if update_submitted:
                    if name and email and header_name and message:
                        updated_data = {
                            'Name': name,
                            'Email': email,
                            'Header Name': header_name,
                            'Due Date': due_date,
                            'Due Time': due_time.strftime('%H:%M'),
                            'Message': message,
                            'Status': status
                        }

                        if update_reminder(st.session_state.edit_reminder_id, updated_data):
                            st.success("✅ Reminder updated successfully!")
                            st.session_state.edit_mode = False
                            st.session_state.edit_reminder_id = None
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to update reminder")
                    else:
                        st.error("❌ Please fill in all required fields")

elif page == "🎯 Selective Mailing":
    st.title("🎯 Selective Mailing")

    df = st.session_state.reminders_df

    if df.empty:
        st.info("No reminders found. Add reminders first.")
    else:
        st.write("Select specific recipients to send reminders to:")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"], key="selective_status")
        with col2:
            search_term = st.text_input("🔍 Search recipients", placeholder="Search by name or email...", key="selective_search")

        # Apply filters
        filtered_df = df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df.get('Status', 'Active') == status_filter]

        if search_term:
            mask = (
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['Email'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]

        if not filtered_df.empty:
            # Multi-select for recipients
            recipient_options = []
            for _, row in filtered_df.iterrows():
                recipient_options.append({
                    'id': row['ID'],
                    'display': f"{row['Name']} ({row['Email']}) - {row['Header Name']}",
                    'name': row['Name'],
                    'email': row['Email'],
                    'header': row['Header Name']
                })

            st.subheader("📋 Select Recipients")

            # Quick selection buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Select All Visible"):
                    st.session_state.selected_for_mailing = [opt['id'] for opt in recipient_options]
                    st.rerun()
            with col2:
                if st.button("❌ Clear Selection"):
                    st.session_state.selected_for_mailing = []
                    st.rerun()
            with col3:
                if st.button("🔄 Refresh"):
                    st.rerun()

            # Initialize selection state
            if 'selected_for_mailing' not in st.session_state:
                st.session_state.selected_for_mailing = []

            # Display recipients with checkboxes
            for opt in recipient_options:
                col1, col2 = st.columns([0.5, 9.5])
                with col1:
                    is_selected = st.checkbox("", key=f"mail_select_{opt['id']}",
                                            value=opt['id'] in st.session_state.selected_for_mailing)
                    if is_selected and opt['id'] not in st.session_state.selected_for_mailing:
                        st.session_state.selected_for_mailing.append(opt['id'])
                    elif not is_selected and opt['id'] in st.session_state.selected_for_mailing:
                        st.session_state.selected_for_mailing.remove(opt['id'])

                with col2:
                    st.write(f"**{opt['name']}** ({opt['email']}) - {opt['agreement']}")

            # Send selected
            if st.session_state.selected_for_mailing:
                st.subheader(f"📤 Send to Selected ({len(st.session_state.selected_for_mailing)} recipients)")

                # Custom message option
                use_custom_message = st.checkbox("📝 Use custom message for this mailing")
                custom_message = ""

                if use_custom_message:
                    custom_message = st.text_area(
                        "Custom Message",
                        placeholder="Enter a custom message for this mailing...",
                        height=100
                    )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📧 Send to Selected Recipients", type="primary"):
                        config = st.session_state.email_config
                        if not config.get('sender_email') or not config.get('app_password'):
                            st.error("❌ Please configure email settings first")
                        else:
                            sent_count = 0
                            failed_count = 0

                            for recipient_id in st.session_state.selected_for_mailing:
                                row = df[df['ID'] == recipient_id].iloc[0]
                                subject = f"Reminder - {row['Header Name']}"

                                if use_custom_message and custom_message:
                                    body = f"Dear {row['Name']},\n\n{custom_message}\n\nRegards,\nAccounts Team"
                                else:
                                    body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"

                                if send_email(row['Email'], subject, body, config['sender_email'], config['app_password']):
                                    # Update last sent
                                    df.loc[df['ID'] == recipient_id, 'Last Sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    sent_count += 1
                                else:
                                    failed_count += 1

                            if sent_count > 0:
                                save_reminders(df)
                                st.session_state.reminders_df = df

                            st.success(f"✅ Sent {sent_count} emails successfully!")
                            if failed_count > 0:
                                st.warning(f"⚠️ {failed_count} emails failed to send")

                            st.session_state.selected_for_mailing = []
                            st.rerun()

                with col2:
                    if st.button("📋 Preview Selected"):
                        st.subheader("👀 Preview Selected Recipients")
                        for recipient_id in st.session_state.selected_for_mailing:
                            row = df[df['ID'] == recipient_id].iloc[0]
                            st.write(f"• **{row['Name']}** ({row['Email']}) - {row['Header Name']}")
            else:
                st.info("👆 Select recipients above to send emails")
        else:
            st.info("No recipients match your filter criteria")

elif page == "⚙️ Email Settings":
    st.title("⚙️ Email Configuration")

    # Check if user has admin privileges
    if not is_admin_logged_in():
        st.error("❌ Please log in as an administrator to access email settings.")
        st.stop()

    # Redirect to Admin Management for email configuration
    st.info("📧 **Email accounts are now managed through Admin Management**")

    st.markdown("""
    ### 🔄 **Email Configuration Has Moved!**

    For better security and centralized management, email account configuration is now handled in the **Admin Management** section.

    **To configure email accounts:**
    1. Go to **👥 Admin Management** (in the sidebar)
    2. Click on **📧 Email Management** tab
    3. Add your email accounts with app passwords
    4. Set a default email for sending reminders

    **Benefits of the new system:**
    - ✅ **Multiple email accounts** support
    - ✅ **Centralized management** by administrators
    - ✅ **Better security** with encrypted storage
    - ✅ **Usage tracking** and statistics
    - ✅ **Connection testing** before saving
    """)

    # Quick navigation button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📧 Go to Email Management", type="primary", help="Navigate to Admin Management → Email Management"):
            st.session_state.page = "👥 Admin Management"
            st.rerun()

    st.divider()

    # Show current email accounts status
    st.markdown("### 📊 **Current Email Accounts Status**")

    try:
        from auth import load_email_accounts
        email_accounts = load_email_accounts()

        if email_accounts:
            st.success(f"✅ {len(email_accounts)} email account(s) configured")

            # Show summary
            for email, data in email_accounts.items():
                status_icon = "🌟" if data.get('is_default') else "📧"
                status_text = "🟢 Active" if data.get('status') == 'active' else "🔴 Inactive"
                sent_count = data.get('total_sent', 0)

                st.markdown(f"**{status_icon} {email}** - {status_text} - Sent: {sent_count} emails")
        else:
            st.warning("⚠️ No email accounts configured yet")
            st.markdown("**Next steps:**")
            st.markdown("1. Click the button above to go to Email Management")
            st.markdown("2. Add your first email account")
            st.markdown("3. Test the connection")
            st.markdown("4. Start sending reminders!")

    except Exception as e:
        st.error(f"❌ Error loading email accounts: {str(e)}")

    # Legacy configuration notice
    st.divider()
    st.markdown("### 📋 **Migration Notice**")
    st.info("""
    **For existing users:** If you had email settings configured in the old system,
    you'll need to re-add them in the new Email Management section.
    This ensures better security and gives you access to new features like multiple email accounts.
    """)

elif page == "📤 Send Now":
    st.title("📤 Send Reminders Now")

    # Check email configuration from admin management
    email_ready = False
    try:
        from auth import get_default_email_account
        default_account = get_default_email_account()
        if default_account:
            email_ready = True
            st.success(f"✅ Email ready: {default_account['email']}")
        else:
            st.error("❌ No email account configured in Admin Management")
            if st.button("Go to Email Management"):
                st.session_state.page = "👥 Admin Management"
                st.rerun()
    except:
        # Fallback to old config system
        config = st.session_state.email_config
        if not config.get('sender_email') or not config.get('app_password'):
            st.error("❌ Please configure email settings first")
            if st.button("Go to Email Settings"):
                st.session_state.page = "⚙️ Email Settings"
                st.rerun()
        else:
            email_ready = True
            st.success("✅ Email configuration is ready")

    if email_ready:
        
        df = st.session_state.reminders_df
        today = datetime.today().date()
        
        if not df.empty:
            # Show today's due reminders
            if 'Due Date' in df.columns:
                due_today_df = df[pd.to_datetime(df['Due Date'], errors='coerce').dt.date == today]
                
                if not due_today_df.empty:
                    st.subheader("📅 Due Today")
                    st.dataframe(due_today_df[['Name', 'Email', 'Header Name', 'Due Date']], use_container_width=True)
                    
                    if st.button("📧 Send All Due Reminders", type="primary"):
                        result = check_and_send_reminders()
                        st.success(f"✅ {result}")
                        st.rerun()
                else:
                    st.info("📅 No reminders due today")
            
            # Manual send section
            st.subheader("📤 Manual Send")
            st.write("Select specific reminders to send manually:")
            
            if not df.empty:
                selected_indices = st.multiselect(
                    "Select reminders to send:",
                    options=df.index,
                    format_func=lambda x: f"{df.loc[x, 'Name']} - {df.loc[x, 'Header Name']}"
                )
                
                if selected_indices and st.button("📧 Send Selected Reminders"):
                    sent_count = 0
                    for idx in selected_indices:
                        row = df.loc[idx]
                        subject = f"Reminder - {row['Header Name']}"
                        body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"
                        
                        if send_email(row['Email'], subject, body, config['sender_email'], config['app_password']):
                            df.at[idx, 'Last Sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            sent_count += 1
                    
                    if sent_count > 0:
                        save_reminders(df)
                        st.session_state.reminders_df = df
                    
                    st.success(f"✅ Sent {sent_count} reminders")
                    st.rerun()
        else:
            st.info("No reminders configured yet")

elif page == "🔧 Scheduler Status":
    st.title("🔧 Scheduler Status & Management")

    # Scheduler information
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Scheduler Information")
        st.info("✅ Background scheduler is running")
        st.write(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Get scheduled jobs
        jobs = get_scheduled_jobs()
        st.metric("📅 Scheduled Jobs", len(jobs))

        if st.button("🔄 Reschedule All Active Reminders"):
            reschedule_all_reminders()
            st.success("✅ All active reminders rescheduled!")
            st.rerun()

    with col2:
        st.subheader("📋 Scheduled Jobs")
        if jobs:
            for job in jobs:
                with st.container():
                    st.write(f"**Job ID:** {job['id']}")
                    st.write(f"**Name:** {job['name']}")
                    if job['next_run']:
                        st.write(f"**Next Run:** {job['next_run'].strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        st.write("**Next Run:** Not scheduled")
                    st.divider()
        else:
            st.info("No jobs currently scheduled")

    # Scheduler logs
    st.subheader("📝 Recent Scheduler Logs")
    log_file = "scheduler.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = f.readlines()

            # Show last 20 lines
            recent_logs = logs[-20:] if len(logs) > 20 else logs
            log_text = ''.join(recent_logs)
            st.text_area("Recent Logs", log_text, height=300)

            if st.button("🗑️ Clear Logs"):
                with open(log_file, 'w') as f:
                    f.write("")
                st.success("✅ Logs cleared!")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading logs: {e}")
    else:
        st.info("No log file found")

elif page == "👥 Admin Management":
    st.title("👥 Admin Management")
    show_admin_management()

# Logout button
st.sidebar.markdown("---")
if is_admin_logged_in():
    if st.sidebar.button("🚪 Logout Admin", type="secondary"):
        from auth import logout_admin
        logout_admin()
        st.rerun()
elif is_user_logged_in():
    if st.sidebar.button("🚪 Logout User", type="secondary"):
        from auth import logout_user
        logout_user()
        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("� **Reminder System**")
st.sidebar.markdown("Built with Streamlit")
if is_admin_logged_in():
    st.sidebar.markdown(f"� Admin: {get_current_admin()}")
elif is_user_logged_in():
    st.sidebar.markdown(f"👤 User: {get_current_user()}")
