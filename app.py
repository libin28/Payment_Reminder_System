import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
import schedule
import time
import threading

# Page configuration
st.set_page_config(
    page_title="Payment Reminder System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
EXCEL_FILE = "payment_reminders.xlsx"
CONFIG_FILE = "email_config.json"

# Initialize session state
if 'reminders_df' not in st.session_state:
    st.session_state.reminders_df = pd.DataFrame()
if 'email_config' not in st.session_state:
    st.session_state.email_config = {}

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
            return df
        else:
            # Create empty DataFrame with required columns
            columns = ['Name', 'Email', 'Agreement Name', 'Due Date', 'Message', 'Status', 'Last Sent']
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

def send_email(recipient, subject, body, sender_email, app_password):
    """Send email reminder"""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

def check_and_send_reminders():
    """Check for due reminders and send them"""
    config = load_email_config()
    if not config.get('sender_email') or not config.get('app_password'):
        return "Email configuration not set"
    
    df = load_reminders()
    if df.empty:
        return "No reminders found"
    
    today = datetime.today().date()
    sent_count = 0
    
    for index, row in df.iterrows():
        if pd.notna(row['Due Date']):
            due_date = pd.to_datetime(row['Due Date']).date()
            if due_date == today and row.get('Status', 'Active') == 'Active':
                subject = f"Payment Reminder - {row['Agreement Name']}"
                body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"
                
                if send_email(row['Email'], subject, body, config['sender_email'], config['app_password']):
                    df.at[index, 'Last Sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sent_count += 1
    
    if sent_count > 0:
        save_reminders(df)
    
    return f"Sent {sent_count} reminders"

# Sidebar navigation
st.sidebar.title("📧 Payment Reminder System")
page = st.sidebar.selectbox("Navigate", [
    "🏠 Dashboard", 
    "➕ Add Reminder", 
    "📋 Manage Reminders", 
    "⚙️ Email Settings",
    "📤 Send Now"
])

# Load data
st.session_state.reminders_df = load_reminders()
st.session_state.email_config = load_email_config()

# Main content based on selected page
if page == "🏠 Dashboard":
    st.title("📊 Payment Reminder Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    df = st.session_state.reminders_df
    
    with col1:
        st.metric("Total Reminders", len(df))
    
    with col2:
        active_count = len(df[df.get('Status', 'Active') == 'Active']) if not df.empty else 0
        st.metric("Active Reminders", active_count)
    
    with col3:
        today = datetime.today().date()
        if not df.empty and 'Due Date' in df.columns:
            due_today = len(df[pd.to_datetime(df['Due Date'], errors='coerce').dt.date == today])
        else:
            due_today = 0
        st.metric("Due Today", due_today)
    
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
        st.metric("Due This Week", upcoming)
    
    # Recent activity
    st.subheader("📅 Upcoming Reminders")
    if not df.empty and 'Due Date' in df.columns:
        upcoming_df = df[pd.to_datetime(df['Due Date'], errors='coerce').dt.date >= today].copy()
        if not upcoming_df.empty:
            upcoming_df['Due Date'] = pd.to_datetime(upcoming_df['Due Date'])
            upcoming_df = upcoming_df.sort_values('Due Date').head(10)
            st.dataframe(upcoming_df[['Name', 'Agreement Name', 'Due Date', 'Email']], use_container_width=True)
        else:
            st.info("No upcoming reminders")
    else:
        st.info("No reminders configured yet")

elif page == "➕ Add Reminder":
    st.title("➕ Add New Payment Reminder")
    
    with st.form("add_reminder_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Contact Name*", placeholder="John Doe")
            email = st.text_input("Email Address*", placeholder="john@example.com")
            agreement_name = st.text_input("Agreement Name*", placeholder="Monthly Rent Payment")
        
        with col2:
            due_date = st.date_input("Due Date*", value=datetime.today().date())
            status = st.selectbox("Status", ["Active", "Inactive"], index=0)
        
        message = st.text_area(
            "Reminder Message*", 
            placeholder="This is a friendly reminder that your payment is due today...",
            height=100
        )
        
        submitted = st.form_submit_button("Add Reminder", type="primary")
        
        if submitted:
            if name and email and agreement_name and message:
                new_reminder = {
                    'Name': name,
                    'Email': email,
                    'Agreement Name': agreement_name,
                    'Due Date': due_date,
                    'Message': message,
                    'Status': status,
                    'Last Sent': ''
                }
                
                df = st.session_state.reminders_df
                new_df = pd.concat([df, pd.DataFrame([new_reminder])], ignore_index=True)
                
                if save_reminders(new_df):
                    st.success("✅ Reminder added successfully!")
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
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search reminders", placeholder="Search by name, email, or agreement...")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col3:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Apply filters
        filtered_df = df.copy()
        if search_term:
            mask = (
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['Email'].str.contains(search_term, case=False, na=False) |
                filtered_df['Agreement Name'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df.get('Status', 'Active') == status_filter]
        
        # Display reminders
        if not filtered_df.empty:
            st.dataframe(
                filtered_df,
                use_container_width=True,
                column_config={
                    "Due Date": st.column_config.DateColumn("Due Date"),
                    "Last Sent": st.column_config.TextColumn("Last Sent"),
                }
            )
            
            # Bulk actions
            st.subheader("Bulk Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Delete Selected", help="This will delete all filtered reminders"):
                    if st.session_state.get('confirm_delete', False):
                        remaining_df = df[~df.index.isin(filtered_df.index)]
                        if save_reminders(remaining_df):
                            st.success(f"✅ Deleted {len(filtered_df)} reminders")
                            st.session_state.reminders_df = remaining_df
                            st.session_state.confirm_delete = False
                            st.rerun()
                    else:
                        st.session_state.confirm_delete = True
                        st.warning("⚠️ Click again to confirm deletion")
            
            with col2:
                if st.button("📧 Send Reminders Now"):
                    config = st.session_state.email_config
                    if config.get('sender_email') and config.get('app_password'):
                        sent_count = 0
                        for _, row in filtered_df.iterrows():
                            subject = f"Payment Reminder - {row['Agreement Name']}"
                            body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"
                            
                            if send_email(row['Email'], subject, body, config['sender_email'], config['app_password']):
                                sent_count += 1
                        
                        st.success(f"✅ Sent {sent_count} reminders")
                    else:
                        st.error("❌ Please configure email settings first")
        else:
            st.info("No reminders match your search criteria")
    else:
        st.info("No reminders found. Add your first reminder using the 'Add Reminder' page.")

elif page == "⚙️ Email Settings":
    st.title("⚙️ Email Configuration")
    
    st.info("📧 Configure your Gmail settings to send automated reminders")
    
    with st.form("email_config_form"):
        sender_email = st.text_input(
            "Gmail Address*", 
            value=st.session_state.email_config.get('sender_email', ''),
            placeholder="your-email@gmail.com"
        )
        
        app_password = st.text_input(
            "App Password*", 
            type="password",
            value=st.session_state.email_config.get('app_password', ''),
            help="Generate an App Password from your Google Account settings"
        )
        
        st.markdown("""
        **How to get Gmail App Password:**
        1. Go to your Google Account settings
        2. Select Security → 2-Step Verification
        3. At the bottom, select App passwords
        4. Generate a password for 'Mail'
        5. Use that 16-character password here
        """)
        
        test_email = st.text_input(
            "Test Email (optional)", 
            placeholder="test@example.com",
            help="Send a test email to verify configuration"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            save_config = st.form_submit_button("💾 Save Configuration", type="primary")
        with col2:
            test_config = st.form_submit_button("📧 Send Test Email")
        
        if save_config:
            if sender_email and app_password:
                config = {
                    'sender_email': sender_email,
                    'app_password': app_password
                }
                save_email_config(config)
                st.session_state.email_config = config
                st.success("✅ Email configuration saved!")
            else:
                st.error("❌ Please fill in all required fields")
        
        if test_config:
            if sender_email and app_password and test_email:
                subject = "Test Email - Payment Reminder System"
                body = "This is a test email from your Payment Reminder System. Configuration is working correctly!"
                
                if send_email(test_email, subject, body, sender_email, app_password):
                    st.success("✅ Test email sent successfully!")
                else:
                    st.error("❌ Failed to send test email. Please check your configuration.")
            else:
                st.error("❌ Please fill in all fields to send test email")

elif page == "📤 Send Now":
    st.title("📤 Send Reminders Now")
    
    config = st.session_state.email_config
    if not config.get('sender_email') or not config.get('app_password'):
        st.error("❌ Please configure email settings first")
        if st.button("Go to Email Settings"):
            st.switch_page("⚙️ Email Settings")
    else:
        st.success("✅ Email configuration is ready")
        
        df = st.session_state.reminders_df
        today = datetime.today().date()
        
        if not df.empty:
            # Show today's due reminders
            if 'Due Date' in df.columns:
                due_today_df = df[pd.to_datetime(df['Due Date'], errors='coerce').dt.date == today]
                
                if not due_today_df.empty:
                    st.subheader("📅 Due Today")
                    st.dataframe(due_today_df[['Name', 'Email', 'Agreement Name', 'Due Date']], use_container_width=True)
                    
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
                    format_func=lambda x: f"{df.loc[x, 'Name']} - {df.loc[x, 'Agreement Name']}"
                )
                
                if selected_indices and st.button("📧 Send Selected Reminders"):
                    sent_count = 0
                    for idx in selected_indices:
                        row = df.loc[idx]
                        subject = f"Payment Reminder - {row['Agreement Name']}"
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

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("💰 **Payment Reminder System**")
st.sidebar.markdown("Built with Streamlit")
