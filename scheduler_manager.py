import logging
import threading
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
import json
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EmailScheduler:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one scheduler instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmailScheduler, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.scheduler = BackgroundScheduler(
            timezone='UTC',
            job_defaults={
                'coalesce': False,
                'max_instances': 3,
                'misfire_grace_time': 300  # 5 minutes grace period
            }
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_missed, EVENT_JOB_MISSED)
        
        self.scheduler.start()
        self._initialized = True
        logger.info("EmailScheduler initialized and started")
    
    def _job_executed(self, event):
        """Handle successful job execution"""
        logger.info(f"Job {event.job_id} executed successfully at {datetime.now()}")
    
    def _job_error(self, event):
        """Handle job execution errors"""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    
    def _job_missed(self, event):
        """Handle missed job executions"""
        logger.warning(f"Job {event.job_id} missed execution time")
    
    def load_email_config(self):
        """Load email configuration from admin management or fallback to old config"""
        try:
            # Try to import and use the new email account system
            import sys
            import base64
            sys.path.append('.')
            from auth import get_default_email_account

            default_account = get_default_email_account()
            if default_account:
                # The password from admin management is base64 encoded, decode it
                password = default_account['password']
                try:
                    # Try to decode if it's base64 encoded
                    decoded_password = base64.b64decode(password).decode('utf-8')
                    password = decoded_password
                except:
                    # If decoding fails, use the password as-is
                    pass

                logger.info(f"Loaded email config from admin management: {default_account['email']}")
                return {
                    'sender_email': default_account['email'],
                    'app_password': password
                }
        except Exception as e:
            logger.warning(f"Could not load from admin management: {e}")

        # Fallback to old config system
        config_file = "email_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded email config from file: {config.get('sender_email', 'N/A')}")
                return config

        logger.error("No email configuration found")
        return {}
    
    def load_reminders(self):
        """Load reminders from Excel file"""
        excel_file = "payment_reminders.xlsx"
        try:
            if os.path.exists(excel_file):
                return pd.read_excel(excel_file, sheet_name="Reminders")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
            return pd.DataFrame()
    
    def save_reminders(self, df):
        """Save reminders to Excel file"""
        excel_file = "payment_reminders.xlsx"
        try:
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Reminders", index=False)
            return True
        except Exception as e:
            logger.error(f"Error saving reminders: {e}")
            return False
    
    def send_email(self, recipient, subject, body, sender_email, app_password):
        """Send email reminder"""
        try:
            logger.info(f"Attempting to send email to {recipient} from {sender_email}")

            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient, msg.as_string())

            logger.info(f"Email sent successfully to {recipient}")

            # Update email usage statistics if using admin management
            try:
                import sys
                sys.path.append('.')
                from auth import load_email_accounts, save_email_accounts
                accounts = load_email_accounts()
                if sender_email in accounts:
                    accounts[sender_email]["total_sent"] = accounts[sender_email].get("total_sent", 0) + 1
                    accounts[sender_email]["last_used"] = datetime.now().isoformat()
                    save_email_accounts(accounts)
                    logger.info(f"Updated email statistics for {sender_email}")
            except Exception as stats_error:
                logger.warning(f"Could not update email statistics: {stats_error}")

            return True
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {e}")
            return False
    
    def send_reminder_email(self, reminder_id):
        """Send a specific reminder email"""
        logger.info(f"Executing scheduled reminder: {reminder_id}")
        
        # Load current data
        config = self.load_email_config()
        df = self.load_reminders()
        
        if not config.get('sender_email') or not config.get('app_password'):
            logger.error("Email configuration not set")
            return False
        
        if df.empty:
            logger.error("No reminders found")
            return False
        
        # Find the specific reminder
        reminder_row = df[df['ID'] == reminder_id]
        if reminder_row.empty:
            logger.error(f"Reminder {reminder_id} not found")
            return False
        
        row = reminder_row.iloc[0]
        
        # Check if reminder is still active
        if row.get('Status', 'Active') != 'Active':
            logger.info(f"Reminder {reminder_id} is inactive, skipping")
            return False
        
        # Send email with proper error handling and field name fallback
        try:
            # Safely get header name with fallback for old data
            header_name = row.get('Header Name', row.get('Agreement Name', 'Reminder'))

            subject = f"Reminder - {header_name}"
            body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"

            logger.info(f"Attempting to send email to {row['Email']} from {config['sender_email']}")

            success = self.send_email(
                row['Email'],
                subject,
                body,
                config['sender_email'],
                config['app_password']
            )

            if success:
                # Update last sent timestamp
                df.loc[df['ID'] == reminder_id, 'Last Sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_reminders(df)
                logger.info(f"Reminder {reminder_id} sent successfully to {row['Email']}")
            else:
                logger.error(f"Failed to send reminder {reminder_id} to {row['Email']}")

            return success

        except Exception as e:
            logger.error(f"Error processing reminder {reminder_id}: {str(e)}")
            return False
    
    def schedule_reminder(self, reminder_id, due_date, due_time):
        """Schedule a reminder email"""
        try:
            # Parse the due date and time
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            if isinstance(due_time, str):
                due_time = datetime.strptime(due_time, '%H:%M').time()
            
            # Combine date and time
            scheduled_datetime = datetime.combine(due_date, due_time)
            
            # Check if the scheduled time is in the future
            if scheduled_datetime <= datetime.now():
                logger.warning(f"Scheduled time {scheduled_datetime} is in the past for reminder {reminder_id}")
                return False
            
            # Create job ID
            job_id = f"reminder_{reminder_id}"
            
            # Remove existing job if it exists
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed existing job {job_id}")
            except:
                pass  # Job doesn't exist, which is fine
            
            # Schedule the job
            job = self.scheduler.add_job(
                func=self.send_reminder_email,
                trigger=DateTrigger(run_date=scheduled_datetime),
                args=[reminder_id],
                id=job_id,
                name=f"Email reminder for {reminder_id}",
                replace_existing=True
            )
            
            logger.info(f"Scheduled reminder {reminder_id} for {scheduled_datetime} (Job ID: {job_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling reminder {reminder_id}: {e}")
            return False
    
    def cancel_reminder(self, reminder_id):
        """Cancel a scheduled reminder"""
        job_id = f"reminder_{reminder_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled reminder {reminder_id}")
            return True
        except Exception as e:
            logger.warning(f"Could not cancel reminder {reminder_id}: {e}")
            return False
    
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time,
                'trigger': str(job.trigger)
            })
        return jobs
    
    def reschedule_all_active_reminders(self):
        """Reschedule all active reminders (useful after app restart)"""
        logger.info("Rescheduling all active reminders...")
        
        df = self.load_reminders()
        if df.empty:
            logger.info("No reminders to reschedule")
            return
        
        scheduled_count = 0
        for _, row in df.iterrows():
            if row.get('Status', 'Active') == 'Active':
                due_date = pd.to_datetime(row['Due Date']).date()
                due_time = row.get('Due Time', '09:00')
                
                # Only reschedule future reminders
                scheduled_datetime = datetime.combine(due_date, datetime.strptime(due_time, '%H:%M').time())
                if scheduled_datetime > datetime.now():
                    if self.schedule_reminder(row['ID'], due_date, due_time):
                        scheduled_count += 1
        
        logger.info(f"Rescheduled {scheduled_count} active reminders")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if hasattr(self, 'scheduler') and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")

# Global scheduler instance
email_scheduler = EmailScheduler()

def get_scheduler():
    """Get the global scheduler instance"""
    return email_scheduler

def schedule_reminder(reminder_id, due_date, due_time):
    """Convenience function to schedule a reminder"""
    return email_scheduler.schedule_reminder(reminder_id, due_date, due_time)

def cancel_reminder(reminder_id):
    """Convenience function to cancel a reminder"""
    return email_scheduler.cancel_reminder(reminder_id)

def get_scheduled_jobs():
    """Convenience function to get scheduled jobs"""
    return email_scheduler.get_scheduled_jobs()

def reschedule_all_reminders():
    """Convenience function to reschedule all reminders"""
    return email_scheduler.reschedule_all_active_reminders()
