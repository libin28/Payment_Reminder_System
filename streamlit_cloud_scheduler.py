
import streamlit as st
import pandas as pd
import json
import smtplib
import ssl
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import time
import threading

class StreamlitCloudScheduler:
    """Scheduler that works with Streamlit Cloud limitations"""
    
    def __init__(self):
        if 'scheduler_thread' not in st.session_state:
            st.session_state.scheduler_thread = None
        if 'scheduler_running' not in st.session_state:
            st.session_state.scheduler_running = False
    
    def check_and_send_due_emails(self):
        """Check for due emails and send them"""
        try:
            # Load reminders
            df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
            
            # Load email config
            with open('email_accounts.json', 'r') as f:
                accounts = json.load(f)
            
            default_account = None
            for email, data in accounts.items():
                if data.get('is_default', False):
                    default_account = data
                    break
            
            if not default_account:
                return
            
            sender_email = default_account['email']
            password = base64.b64decode(default_account['password']).decode('utf-8')
            
            now = datetime.now()
            sent_count = 0
            
            for index, row in df.iterrows():
                if row.get('Status', 'Active') == 'Active':
                    try:
                        due_date = pd.to_datetime(row['Due Date']).date()
                        due_time_str = row.get('Due Time', '09:00')
                        due_time = datetime.strptime(due_time_str, '%H:%M').time()
                        
                        scheduled_datetime = datetime.combine(due_date, due_time)
                        
                        # Check if it's time to send (within 2 minute window)
                        time_diff = abs((now - scheduled_datetime).total_seconds())

                        if time_diff <= 120 and (pd.isna(row.get('Last Sent', '')) or row.get('Last Sent', '') == ''):
                            # Send email
                            if self.send_email(row['Email'],
                                             f"Reminder - {row['Header Name']}",
                                             f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team",
                                             sender_email, password):

                                # Update last sent
                                df.at[index, 'Last Sent'] = now.strftime('%Y-%m-%d %H:%M:%S')
                                sent_count += 1

                                # Log the sending
                                st.success(f"📧 Email sent to {row['Name']} ({row['Email']})")
                    except:
                        continue
            
            if sent_count > 0:
                # Save updated dataframe
                with pd.ExcelWriter('payment_reminders.xlsx', engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Reminders', index=False)
            
            return sent_count
            
        except Exception as e:
            st.error(f"Scheduler error: {e}")
            return 0
    
    def send_email(self, recipient, subject, body, sender_email, password):
        """Send email with enhanced SMTP"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient
            
            # Try TLS first (better for external emails)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, recipient, msg.as_string())
                server.quit()
                return True
            except:
                # Fallback to SSL
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, recipient, msg.as_string())
                server.quit()
                return True
                
        except Exception as e:
            return False
    
    def start_scheduler(self):
        """Start the scheduler in Streamlit Cloud"""
        if not st.session_state.scheduler_running:
            st.session_state.scheduler_running = True
            
            def scheduler_loop():
                while st.session_state.scheduler_running:
                    try:
                        self.check_and_send_due_emails()
                        time.sleep(30)  # Check every 30 seconds
                    except:
                        break
            
            if st.session_state.scheduler_thread is None or not st.session_state.scheduler_thread.is_alive():
                st.session_state.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
                st.session_state.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        st.session_state.scheduler_running = False

    def get_due_reminders(self):
        """Get reminders that are due now"""
        try:
            df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
            now = datetime.now()
            due_reminders = []

            for _, row in df.iterrows():
                if row.get('Status', 'Active') == 'Active':
                    try:
                        due_date = pd.to_datetime(row['Due Date']).date()
                        due_time_str = row.get('Due Time', '09:00')
                        due_time = datetime.strptime(due_time_str, '%H:%M').time()

                        scheduled_datetime = datetime.combine(due_date, due_time)

                        # Check if it's due (within 2 minute window)
                        time_diff = (now - scheduled_datetime).total_seconds()

                        if -120 <= time_diff <= 120 and (pd.isna(row.get('Last Sent', '')) or row.get('Last Sent', '') == ''):
                            due_reminders.append({
                                'name': row['Name'],
                                'email': row['Email'],
                                'subject': row['Header Name'],
                                'scheduled_time': scheduled_datetime,
                                'time_diff': time_diff
                            })
                    except:
                        continue

            return due_reminders
        except:
            return []

# Global scheduler instance
if 'cloud_scheduler' not in st.session_state:
    st.session_state.cloud_scheduler = StreamlitCloudScheduler()

def get_cloud_scheduler():
    """Get the cloud scheduler instance"""
    return st.session_state.cloud_scheduler

def show_cloud_scheduler_status():
    """Show cloud scheduler status and controls"""
    st.subheader("🤖 Cloud Scheduler Status")

    cloud_scheduler = get_cloud_scheduler()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.get('scheduler_running', False):
            st.success("🟢 Status: Running")
        else:
            st.warning("🟡 Status: Stopped")

    with col2:
        if st.button("🔄 Check Due Emails Now"):
            with st.spinner("Checking for due emails..."):
                sent_count = cloud_scheduler.check_and_send_due_emails()
                if sent_count > 0:
                    st.success(f"📧 Sent {sent_count} due emails!")
                else:
                    st.info("ℹ️ No emails due at this time")

    with col3:
        if st.session_state.get('scheduler_running', False):
            if st.button("⏹️ Stop Scheduler"):
                cloud_scheduler.stop_scheduler()
                st.rerun()
        else:
            if st.button("▶️ Start Scheduler"):
                cloud_scheduler.start_scheduler()
                st.rerun()

    # Show due reminders
    due_reminders = cloud_scheduler.get_due_reminders()
    if due_reminders:
        st.subheader("⏰ Due Reminders")
        for reminder in due_reminders:
            st.info(f"📧 {reminder['name']} ({reminder['email']}) - Due: {reminder['scheduled_time'].strftime('%Y-%m-%d %H:%M')}")

def initialize_cloud_scheduler():
    """Initialize scheduler for Streamlit Cloud"""
    if 'cloud_scheduler_initialized' not in st.session_state:
        st.session_state.cloud_scheduler_initialized = True

        # Start the cloud scheduler
        cloud_scheduler = get_cloud_scheduler()
        cloud_scheduler.start_scheduler()

        st.success("✅ Cloud scheduler initialized!")

        # Show current time for reference
        st.info(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
