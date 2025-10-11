#!/usr/bin/env python3
"""
Fix automatic scheduling for Streamlit Cloud deployment
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import threading
import uuid

def create_streamlit_cloud_scheduler():
    """Create a scheduler that works with Streamlit Cloud"""
    
    scheduler_code = '''
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
                        
                        # Check if it's time to send (within 1 minute window)
                        time_diff = abs((now - scheduled_datetime).total_seconds())
                        
                        if time_diff <= 60 and pd.isna(row.get('Last Sent', '')):
                            # Send email
                            if self.send_email(row['Email'], 
                                             f"Reminder - {row['Header Name']}", 
                                             f"Dear {row['Name']},\\n\\n{row['Message']}\\n\\nRegards,\\nAccounts Team",
                                             sender_email, password):
                                
                                # Update last sent
                                df.at[index, 'Last Sent'] = now.strftime('%Y-%m-%d %H:%M:%S')
                                sent_count += 1
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

# Global scheduler instance
if 'cloud_scheduler' not in st.session_state:
    st.session_state.cloud_scheduler = StreamlitCloudScheduler()

def get_cloud_scheduler():
    """Get the cloud scheduler instance"""
    return st.session_state.cloud_scheduler
'''
    
    return scheduler_code

def create_streamlit_cloud_integration():
    """Create integration code for Streamlit Cloud"""
    
    integration_code = '''
# Add this to your app.py for Streamlit Cloud compatibility

# At the top of app.py, after imports:
from streamlit_cloud_scheduler import get_cloud_scheduler

# In your main app logic, add this:
def initialize_cloud_scheduler():
    """Initialize scheduler for Streamlit Cloud"""
    if 'cloud_scheduler_initialized' not in st.session_state:
        st.session_state.cloud_scheduler_initialized = True
        
        # Start the cloud scheduler
        cloud_scheduler = get_cloud_scheduler()
        cloud_scheduler.start_scheduler()
        
        st.success("✅ Cloud scheduler initialized!")

# Call this in your main app
initialize_cloud_scheduler()

# Add scheduler status to your sidebar or main page:
def show_cloud_scheduler_status():
    """Show cloud scheduler status"""
    cloud_scheduler = get_cloud_scheduler()
    
    if st.session_state.get('scheduler_running', False):
        st.success("🟢 Cloud Scheduler: Running")
        
        if st.button("🔄 Check Due Emails Now"):
            sent_count = cloud_scheduler.check_and_send_due_emails()
            if sent_count > 0:
                st.success(f"📧 Sent {sent_count} due emails!")
            else:
                st.info("ℹ️ No emails due at this time")
    else:
        st.warning("🟡 Cloud Scheduler: Stopped")
        if st.button("▶️ Start Cloud Scheduler"):
            cloud_scheduler.start_scheduler()
            st.rerun()
'''
    
    return integration_code

def create_requirements_txt():
    """Create requirements.txt for Streamlit Cloud"""
    
    requirements = '''streamlit>=1.28.0
pandas>=1.5.0
openpyxl>=3.0.0
bcrypt>=4.0.0
APScheduler>=3.10.0
email-validator>=2.0.0
'''
    
    return requirements

def create_deployment_guide():
    """Create deployment guide for Streamlit Cloud"""
    
    guide = '''
# 🚀 STREAMLIT CLOUD DEPLOYMENT GUIDE

## ❌ PROBLEM WITH STREAMLIT CLOUD:
Streamlit Cloud doesn't support persistent background processes like APScheduler.
The scheduler gets reset when the app restarts or goes idle.

## ✅ SOLUTION: CLOUD-COMPATIBLE SCHEDULER

### 1. 📁 FILES TO ADD TO YOUR REPOSITORY:

**streamlit_cloud_scheduler.py** - Cloud-compatible scheduler
**requirements.txt** - Updated dependencies

### 2. 🔧 MODIFY YOUR app.py:

Add these lines at the top:
```python
from streamlit_cloud_scheduler import get_cloud_scheduler
```

Add this function:
```python
def initialize_cloud_scheduler():
    if 'cloud_scheduler_initialized' not in st.session_state:
        st.session_state.cloud_scheduler_initialized = True
        cloud_scheduler = get_cloud_scheduler()
        cloud_scheduler.start_scheduler()
        st.success("✅ Cloud scheduler initialized!")

# Call this in your main app
initialize_cloud_scheduler()
```

### 3. 📊 ADD SCHEDULER STATUS:

```python
def show_cloud_scheduler_status():
    cloud_scheduler = get_cloud_scheduler()
    
    if st.session_state.get('scheduler_running', False):
        st.success("🟢 Cloud Scheduler: Running")
        
        if st.button("🔄 Check Due Emails Now"):
            sent_count = cloud_scheduler.check_and_send_due_emails()
            if sent_count > 0:
                st.success(f"📧 Sent {sent_count} due emails!")
            else:
                st.info("ℹ️ No emails due at this time")
    else:
        st.warning("🟡 Cloud Scheduler: Stopped")
        if st.button("▶️ Start Cloud Scheduler"):
            cloud_scheduler.start_scheduler()
            st.rerun()
```

### 4. 🎯 HOW IT WORKS:

1. **Thread-based Scheduler**: Uses threading instead of APScheduler
2. **Session State**: Maintains state across Streamlit reruns
3. **Manual Trigger**: Button to manually check for due emails
4. **Auto-restart**: Restarts when app wakes up from idle

### 5. 📧 USAGE IN STREAMLIT CLOUD:

1. **Automatic**: Checks every 30 seconds for due emails
2. **Manual**: Click "Check Due Emails Now" button
3. **Monitoring**: Shows scheduler status in real-time

### 6. ⚠️ LIMITATIONS:

- **App Idle**: When app goes idle, scheduler stops
- **Manual Restart**: Need to restart scheduler when app wakes up
- **Visitor Dependent**: Works best with regular app visitors

### 7. 🎊 BENEFITS:

- **Works on Streamlit Cloud**: Compatible with cloud limitations
- **No External Services**: No need for external cron jobs
- **Real-time Control**: Manual trigger for immediate sending
- **Session Persistent**: Maintains state during app usage

## 🚀 DEPLOYMENT STEPS:

1. Add streamlit_cloud_scheduler.py to your repo
2. Update requirements.txt
3. Modify app.py with integration code
4. Deploy to Streamlit Cloud
5. Test with manual trigger button
6. Monitor scheduler status

Your automatic emails will work on Streamlit Cloud! 🎉
'''
    
    return guide

def main():
    """Main function to create Streamlit Cloud fix"""
    print("🚀 CREATING STREAMLIT CLOUD SCHEDULER FIX")
    print("=" * 50)
    
    # Create scheduler file
    scheduler_code = create_streamlit_cloud_scheduler()
    with open('streamlit_cloud_scheduler.py', 'w') as f:
        f.write(scheduler_code)
    print("✅ Created streamlit_cloud_scheduler.py")
    
    # Create integration code
    integration_code = create_streamlit_cloud_integration()
    with open('streamlit_cloud_integration.py', 'w') as f:
        f.write(integration_code)
    print("✅ Created streamlit_cloud_integration.py")
    
    # Create requirements.txt
    requirements = create_requirements_txt()
    with open('requirements_cloud.txt', 'w') as f:
        f.write(requirements)
    print("✅ Created requirements_cloud.txt")
    
    # Create deployment guide
    guide = create_deployment_guide()
    with open('STREAMLIT_CLOUD_DEPLOYMENT_GUIDE.md', 'w') as f:
        f.write(guide)
    print("✅ Created STREAMLIT_CLOUD_DEPLOYMENT_GUIDE.md")
    
    print(f"\n🎉 STREAMLIT CLOUD FIX CREATED!")
    print(f"📁 Files created:")
    print(f"   - streamlit_cloud_scheduler.py")
    print(f"   - streamlit_cloud_integration.py") 
    print(f"   - requirements_cloud.txt")
    print(f"   - STREAMLIT_CLOUD_DEPLOYMENT_GUIDE.md")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Add these files to your GitHub repository")
    print(f"2. Update your app.py with the integration code")
    print(f"3. Update requirements.txt")
    print(f"4. Redeploy to Streamlit Cloud")
    print(f"5. Test the manual trigger button")

if __name__ == "__main__":
    main()
