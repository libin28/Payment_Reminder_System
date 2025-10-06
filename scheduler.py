import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
import json
import schedule
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reminder_scheduler.log'),
        logging.StreamHandler()
    ]
)

# Constants
EXCEL_FILE = "payment_reminders.xlsx"
CONFIG_FILE = "email_config.json"
LOG_FILE = "sent_reminders.log"

def load_email_config():
    """Load email configuration from file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            logging.warning("Email configuration file not found")
            return {}
    except Exception as e:
        logging.error(f"Error loading email config: {str(e)}")
        return {}

def load_reminders():
    """Load reminders from Excel file"""
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE, sheet_name="Reminders")
            return df
        else:
            logging.warning("Reminders Excel file not found")
            return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error loading reminders: {str(e)}")
        return pd.DataFrame()

def save_reminders(df):
    """Save reminders to Excel file"""
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Reminders", index=False)
        return True
    except Exception as e:
        logging.error(f"Error saving reminders: {str(e)}")
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
        
        logging.info(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        logging.error(f"Error sending email to {recipient}: {str(e)}")
        return False

def log_sent_reminder(name, email, agreement, date_sent):
    """Log sent reminder to file"""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(f"{date_sent},{name},{email},{agreement}\n")
    except Exception as e:
        logging.error(f"Error logging sent reminder: {str(e)}")

def check_and_send_reminders():
    """Check for due reminders and send them"""
    logging.info("Checking for due reminders...")
    
    # Load configuration
    config = load_email_config()
    if not config.get('sender_email') or not config.get('app_password'):
        logging.error("Email configuration not set")
        return
    
    # Load reminders
    df = load_reminders()
    if df.empty:
        logging.info("No reminders found")
        return
    
    today = datetime.today().date()
    sent_count = 0
    
    for index, row in df.iterrows():
        try:
            if pd.notna(row['Due Date']):
                due_date = pd.to_datetime(row['Due Date']).date()
                
                # Check if reminder is due today and is active
                if due_date == today and row.get('Status', 'Active') == 'Active':
                    subject = f"Payment Reminder - {row['Agreement Name']}"
                    body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"
                    
                    if send_email(row['Email'], subject, body, config['sender_email'], config['app_password']):
                        # Update last sent timestamp
                        df.at[index, 'Last Sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        sent_count += 1
                        
                        # Log the sent reminder
                        log_sent_reminder(
                            row['Name'], 
                            row['Email'], 
                            row['Agreement Name'], 
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        )
                        
                        logging.info(f"Reminder sent to {row['Name']} ({row['Email']}) for {row['Agreement Name']}")
                    else:
                        logging.error(f"Failed to send reminder to {row['Name']} ({row['Email']})")
        
        except Exception as e:
            logging.error(f"Error processing reminder for row {index}: {str(e)}")
    
    # Save updated reminders if any were sent
    if sent_count > 0:
        if save_reminders(df):
            logging.info(f"Successfully sent {sent_count} reminders and updated records")
        else:
            logging.error(f"Sent {sent_count} reminders but failed to update records")
    else:
        logging.info("No reminders were due today")

def check_monthly_recurring():
    """Check for monthly recurring reminders and create new entries"""
    logging.info("Checking for monthly recurring reminders...")
    
    df = load_reminders()
    if df.empty:
        return
    
    today = datetime.today().date()
    new_reminders = []
    
    for _, row in df.iterrows():
        try:
            if pd.notna(row['Due Date']) and row.get('Status', 'Active') == 'Active':
                due_date = pd.to_datetime(row['Due Date']).date()
                
                # If the due date has passed, create next month's reminder
                if due_date < today:
                    # Calculate next month's due date
                    if due_date.month == 12:
                        next_due = due_date.replace(year=due_date.year + 1, month=1)
                    else:
                        next_due = due_date.replace(month=due_date.month + 1)
                    
                    # Check if we already have a reminder for next month
                    existing_next_month = df[
                        (df['Name'] == row['Name']) & 
                        (df['Agreement Name'] == row['Agreement Name']) &
                        (pd.to_datetime(df['Due Date']).dt.date == next_due)
                    ]
                    
                    if existing_next_month.empty:
                        new_reminder = row.copy()
                        new_reminder['Due Date'] = next_due
                        new_reminder['Last Sent'] = ''
                        new_reminders.append(new_reminder)
                        
                        logging.info(f"Created recurring reminder for {row['Name']} - {row['Agreement Name']} due {next_due}")
        
        except Exception as e:
            logging.error(f"Error processing recurring reminder: {str(e)}")
    
    # Add new reminders to DataFrame
    if new_reminders:
        new_df = pd.concat([df, pd.DataFrame(new_reminders)], ignore_index=True)
        if save_reminders(new_df):
            logging.info(f"Added {len(new_reminders)} recurring reminders")
        else:
            logging.error("Failed to save recurring reminders")

def run_scheduler():
    """Run the scheduler"""
    logging.info("Starting Payment Reminder Scheduler...")
    
    # Schedule daily check at 9:00 AM
    schedule.every().day.at("09:00").do(check_and_send_reminders)
    
    # Schedule monthly recurring check at 9:30 AM on the 1st of each month
    schedule.every().day.at("09:30").do(check_monthly_recurring)
    
    # Also run immediately on startup for testing
    logging.info("Running initial check...")
    check_and_send_reminders()
    check_monthly_recurring()
    
    logging.info("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Scheduler error: {str(e)}")

if __name__ == "__main__":
    # Create log file header if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.write("Date Sent,Name,Email,Agreement Name\n")
    
    run_scheduler()
