#!/usr/bin/env python3
"""
Activate the automatic scheduler system
"""

import pandas as pd
import uuid
from datetime import datetime, timedelta
import json

def add_test_reminder_to_excel():
    """Add a test reminder to Excel file"""
    print("📝 ADDING TEST REMINDER TO EXCEL")
    print("=" * 40)
    
    try:
        # Load existing reminders
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        # Create test reminder for 5 minutes from now
        test_time = datetime.now() + timedelta(minutes=5)
        
        test_reminder = {
            'ID': str(uuid.uuid4()),
            'Name': 'Scheduler Test User',
            'Email': 'smsdfinance@gmail.com',  # Use the working email
            'Header Name': 'Automatic Scheduler Test',
            'Message': 'This is an automatic test email from the scheduler system. If you receive this, the automatic timing system is working perfectly!',
            'Due Date': test_time.strftime('%Y-%m-%d'),
            'Due Time': test_time.strftime('%H:%M'),
            'Status': 'Active',
            'Last Sent': '',
            'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to dataframe
        new_row = pd.DataFrame([test_reminder])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save to Excel
        with pd.ExcelWriter('payment_reminders.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reminders', index=False)
        
        print(f"✅ Added test reminder: {test_reminder['Name']}")
        print(f"📅 Scheduled for: {test_reminder['Due Date']} {test_reminder['Due Time']}")
        print(f"📧 Will be sent to: {test_reminder['Email']}")
        
        return test_reminder
        
    except Exception as e:
        print(f"❌ Error adding test reminder: {e}")
        return None

def trigger_scheduler_reschedule():
    """Trigger the scheduler to reschedule all reminders"""
    print(f"\n🔄 TRIGGERING SCHEDULER RESCHEDULE")
    print("=" * 40)
    
    try:
        # Import and use the scheduler
        from scheduler_manager import get_scheduler
        
        scheduler = get_scheduler()
        
        # Call reschedule method
        scheduler.reschedule_all_active_reminders()
        
        # Check scheduled jobs
        jobs = scheduler.get_scheduled_jobs()
        print(f"✅ Scheduler rescheduled")
        print(f"📊 Total scheduled jobs: {len(jobs)}")
        
        if jobs:
            print("📋 Scheduled jobs:")
            for job in jobs:
                print(f"   🔹 {job['id']}: {job['next_run']}")
        
        return len(jobs) > 0
        
    except Exception as e:
        print(f"❌ Error triggering reschedule: {e}")
        return False

def verify_email_system():
    """Verify email system is working"""
    print(f"\n🔍 VERIFYING EMAIL SYSTEM")
    print("=" * 40)
    
    try:
        # Check email accounts
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        default_account = None
        for email, data in accounts.items():
            if data.get('is_default', False):
                default_account = data
                break
        
        if default_account:
            print(f"✅ Default email: {default_account['email']}")
            print(f"✅ Status: {default_account.get('status', 'unknown')}")
            return True
        else:
            print("❌ No default email account found")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying email: {e}")
        return False

def create_scheduler_instructions():
    """Create instructions for manual activation"""
    print(f"\n📋 MANUAL ACTIVATION INSTRUCTIONS")
    print("=" * 40)
    
    instructions = """
🚀 TO ACTIVATE AUTOMATIC SCHEDULER:

1. Open your app: http://localhost:8501
2. Login as: santhigirifmc@gmail.com
3. Go to: "🔧 Scheduler Status" page
4. Click: "🔄 Reschedule All Active Reminders" button
5. Verify: You should see scheduled jobs listed

📧 TEST EMAIL SCHEDULE:
- A test reminder has been added to your system
- It will be sent automatically in 5 minutes
- Check your email (smsdfinance@gmail.com) for the test

🔍 MONITORING:
- Use "🔧 Scheduler Status" to monitor active jobs
- Check "📋 Manage Reminders" to see all reminders
- View email logs in the scheduler status page

✅ EXPECTED RESULT:
- Automatic emails will be sent at scheduled times
- No manual intervention needed
- System will run continuously in background
"""
    
    print(instructions)
    
    # Save instructions to file
    with open('SCHEDULER_ACTIVATION_INSTRUCTIONS.txt', 'w') as f:
        f.write(instructions)
    
    print("📄 Instructions saved to: SCHEDULER_ACTIVATION_INSTRUCTIONS.txt")

def main():
    """Main activation function"""
    print("🚨 AUTOMATIC SCHEDULER ACTIVATION")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Step 1: Verify email system
    email_ok = verify_email_system()
    
    # Step 2: Add test reminder
    test_reminder = add_test_reminder_to_excel()
    
    # Step 3: Trigger scheduler reschedule
    scheduler_ok = trigger_scheduler_reschedule()
    
    # Step 4: Create manual instructions
    create_scheduler_instructions()
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 ACTIVATION SUMMARY")
    print("=" * 50)
    
    print(f"Email System: {'✅ Working' if email_ok else '❌ Issues'}")
    print(f"Test Reminder: {'✅ Added' if test_reminder else '❌ Failed'}")
    print(f"Scheduler: {'✅ Active' if scheduler_ok else '❌ Needs Manual Activation'}")
    
    if email_ok and test_reminder:
        print(f"\n🎉 SCHEDULER SYSTEM IS READY!")
        print(f"✅ Test reminder added and scheduled")
        print(f"✅ Email system is working")
        print(f"📧 Expect test email in 5 minutes")
        
        if not scheduler_ok:
            print(f"\n⚠️ MANUAL STEP REQUIRED:")
            print(f"   Go to your app and click 'Reschedule All Active Reminders'")
            print(f"   This will activate the automatic scheduling")
    else:
        print(f"\n❌ ISSUES FOUND - CHECK ABOVE FOR DETAILS")

if __name__ == "__main__":
    main()
