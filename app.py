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
    """Enhanced email sending with multiple SMTP configurations for better external email support"""
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

        # Try multiple SMTP configurations for better compatibility
        smtp_configs = [
            {'host': 'smtp.gmail.com', 'port': 587, 'use_tls': True},  # TLS - better for external emails
            {'host': 'smtp.gmail.com', 'port': 465, 'use_ssl': True}   # SSL - fallback
        ]

        last_error = None
        for config in smtp_configs:
            try:
                if config.get('use_ssl'):
                    # SSL connection
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(config['host'], config['port'], context=context)
                else:
                    # TLS connection
                    server = smtplib.SMTP(config['host'], config['port'])
                    if config.get('use_tls'):
                        server.starttls()

                # Login and send
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient, msg.as_string())
                server.quit()

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
                last_error = e
                try:
                    server.quit()
                except:
                    pass
                continue

        # If all configurations failed, show the last error
        st.error(f"Error sending email to {recipient}: {last_error}")
        return False

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
from streamlit_cloud_scheduler import get_cloud_scheduler, show_cloud_scheduler_status, initialize_cloud_scheduler
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
    
def setup_cloud_scheduler():
    """Setup cloud scheduler for automatic emails"""
    if 'cloud_scheduler_setup' not in st.session_state:
        st.session_state.cloud_scheduler_setup = True
        initialize_cloud_scheduler()

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

elif page == "🔧 Scheduler Status":
        st.title("🔧 Scheduler Status")
        
        # Show cloud scheduler status
        show_cloud_scheduler_status()
        
        # Show current time
        st.info(f"🕐 Current Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show reminders summary
        try:
            df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
            active_reminders = df[df.get('Status', 'Active') == 'Active']
            st.metric("📋 Active Reminders", len(active_reminders))
            
            # Show next few due reminders
            now = datetime.now()
            upcoming = []
            for _, row in active_reminders.iterrows():
                try:
                    due_date = pd.to_datetime(row['Due Date']).date()
                    due_time = datetime.strptime(row.get('Due Time', '09:00'), '%H:%M').time()
                    scheduled_datetime = datetime.combine(due_date, due_time)
                    
                    if scheduled_datetime > now and (pd.isna(row.get('Last Sent', '')) or row.get('Last Sent', '') == ''):
                        upcoming.append({
                            'name': row['Name'],
                            'email': row['Email'],
                            'time': scheduled_datetime
                        })
                except:
                    continue
            
            upcoming.sort(key=lambda x: x['time'])
            
            if upcoming:
                st.subheader("📅 Upcoming Reminders")
                for reminder in upcoming[:5]:
                    st.info(f"📧 {reminder['name']} ({reminder['email']}) - {reminder['time'].strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            st.error(f"Error loading reminders: {e}")


