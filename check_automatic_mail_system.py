#!/usr/bin/env python3
"""
Check and fix automatic mail sending system
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from scheduler_manager import get_scheduler
import uuid

def check_scheduler_status():
    """Check if scheduler is running properly"""
    print("🔍 CHECKING SCHEDULER STATUS")
    print("=" * 40)
    
    try:
        scheduler = get_scheduler()
        print(f"✅ Scheduler running: {scheduler.scheduler.running}")
        
        jobs = scheduler.get_scheduled_jobs()
        print(f"📅 Scheduled jobs: {len(jobs)}")
        
        if jobs:
            print("\n📋 Current scheduled jobs:")
            for job in jobs:
                print(f"   🔹 {job['id']}: {job['next_run']}")
        else:
            print("⚠️ No jobs currently scheduled")
        
        return True, len(jobs)
    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        return False, 0

def check_email_configuration():
    """Check email configuration"""
    print(f"\n🔍 CHECKING EMAIL CONFIGURATION")
    print("=" * 40)
    
    try:
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
        print(f"❌ Email config error: {e}")
        return False

def create_test_automatic_reminder():
    """Create a test reminder for automatic sending"""
    print(f"\n📝 CREATING TEST AUTOMATIC REMINDER")
    print("=" * 40)
    
    try:
        # Load existing reminders
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        # Create test reminder for 2 minutes from now
        test_time = datetime.now() + timedelta(minutes=2)
        
        test_reminder = {
            'ID': str(uuid.uuid4()),
            'Name': 'Automatic Test User',
            'Email': 'smsdfinance@gmail.com',  # Use working email for test
            'Header Name': 'Automatic Mail System Test',
            'Message': f'''This is an automatic test email to verify the automatic mail sending system.

Test Details:
- Scheduled Time: {test_time.strftime('%Y-%m-%d %H:%M:%S')}
- System: Automatic Mail Sending
- Status: If you receive this, automatic sending is working!

This email was sent automatically by the scheduler system.''',
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
        
        print(f"✅ Created test reminder:")
        print(f"   📧 To: {test_reminder['Email']}")
        print(f"   📅 Scheduled: {test_reminder['Due Date']} {test_reminder['Due Time']}")
        print(f"   📝 Subject: {test_reminder['Header Name']}")
        
        return test_reminder
    except Exception as e:
        print(f"❌ Error creating test reminder: {e}")
        return None

def schedule_test_reminder(test_reminder):
    """Schedule the test reminder"""
    print(f"\n📅 SCHEDULING TEST REMINDER")
    print("=" * 40)
    
    try:
        scheduler = get_scheduler()
        
        due_date = datetime.strptime(test_reminder['Due Date'], '%Y-%m-%d').date()
        due_time = test_reminder['Due Time']
        
        success = scheduler.schedule_reminder(test_reminder['ID'], due_date, due_time)
        
        if success:
            print(f"✅ Test reminder scheduled successfully!")
            print(f"⏰ Will send at: {test_reminder['Due Date']} {test_reminder['Due Time']}")
            
            # Verify in job queue
            jobs = scheduler.get_scheduled_jobs()
            test_job = [job for job in jobs if test_reminder['ID'] in job['id']]
            
            if test_job:
                print(f"✅ Confirmed in scheduler queue")
                print(f"   Next run: {test_job[0]['next_run']}")
                return True
            else:
                print("⚠️ Not found in scheduler queue")
                return False
        else:
            print(f"❌ Failed to schedule test reminder")
            return False
    except Exception as e:
        print(f"❌ Scheduling error: {e}")
        return False

def check_app_auto_schedule_feature():
    """Check if auto-schedule feature is working in app.py"""
    print(f"\n🔍 CHECKING AUTO-SCHEDULE FEATURE IN APP")
    print("=" * 40)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for auto-schedule checkbox
        if 'auto_schedule' in content and 'Auto-Schedule' in content:
            print("✅ Auto-schedule checkbox found in app")
        else:
            print("⚠️ Auto-schedule checkbox not found")
        
        # Check for scheduling logic
        if 'schedule_reminder(' in content:
            print("✅ Scheduling logic found in app")
        else:
            print("⚠️ Scheduling logic not found")
        
        # Check for proper integration
        if 'if auto_schedule and status == \'Active\':' in content:
            print("✅ Auto-schedule integration working")
            return True
        else:
            print("⚠️ Auto-schedule integration may have issues")
            return False
            
    except Exception as e:
        print(f"❌ Error checking app: {e}")
        return False

def provide_step_by_step_guide():
    """Provide detailed step-by-step guide"""
    print(f"\n📋 STEP-BY-STEP AUTOMATIC MAIL SENDING GUIDE")
    print("=" * 50)
    
    guide = """
🚀 HOW TO SET UP AUTOMATIC MAIL SENDING:

1. 🌐 OPEN YOUR APP:
   - Go to: http://localhost:8501
   - Login as: santhigirifmc@gmail.com

2. ➕ ADD NEW REMINDER:
   - Click "➕ Add Reminder" in sidebar
   - Fill in all details:
     * Name: Recipient's name
     * Email: Recipient's email address
     * Header Name: Email subject/title
     * Message: Your reminder message
     * Due Date: When to send (future date)
     * Due Time: Exact time (e.g., 09:00, 14:30)
     * Status: Keep as "Active"
     * ✅ Auto-Schedule: CHECK THIS BOX!

3. 💾 SAVE REMINDER:
   - Click "Add Reminder" button
   - System will automatically schedule it

4. ✅ VERIFY SCHEDULING:
   - Go to "🔧 Scheduler Status"
   - Check your reminder appears in scheduled jobs
   - Verify the next run time

5. 📧 AUTOMATIC SENDING:
   - Email will be sent automatically at scheduled time
   - No manual intervention needed
   - Check "📋 Manage Reminders" for status

🎯 IMPORTANT TIPS:
- Always check "Auto-Schedule" checkbox
- Use future dates/times only
- Keep status as "Active"
- Monitor "Scheduler Status" page
"""
    
    print(guide)

def main():
    """Main check and fix function"""
    print("🚨 AUTOMATIC MAIL SENDING SYSTEM CHECK")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Step 1: Check scheduler
    scheduler_ok, job_count = check_scheduler_status()
    
    # Step 2: Check email config
    email_ok = check_email_configuration()
    
    # Step 3: Check app auto-schedule feature
    app_ok = check_app_auto_schedule_feature()
    
    # Step 4: Create and schedule test reminder
    if scheduler_ok and email_ok:
        test_reminder = create_test_automatic_reminder()
        if test_reminder:
            schedule_ok = schedule_test_reminder(test_reminder)
        else:
            schedule_ok = False
    else:
        schedule_ok = False
    
    # Step 5: Provide guide
    provide_step_by_step_guide()
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 AUTOMATIC MAIL SYSTEM STATUS")
    print("=" * 50)
    
    print(f"Scheduler: {'✅ Running' if scheduler_ok else '❌ Issues'}")
    print(f"Email Config: {'✅ Working' if email_ok else '❌ Issues'}")
    print(f"App Integration: {'✅ Working' if app_ok else '❌ Issues'}")
    print(f"Test Scheduling: {'✅ Working' if schedule_ok else '❌ Issues'}")
    print(f"Current Jobs: {job_count}")
    
    if all([scheduler_ok, email_ok, app_ok, schedule_ok]):
        print(f"\n🎉 AUTOMATIC MAIL SENDING IS WORKING!")
        print(f"✅ System is ready for automatic email sending")
        print(f"✅ Follow the guide above to add automatic reminders")
        print(f"✅ Test email will be sent in 2 minutes")
    else:
        print(f"\n⚠️ ISSUES FOUND - NEED TO FIX:")
        if not scheduler_ok:
            print("   - Scheduler not running properly")
        if not email_ok:
            print("   - Email configuration issues")
        if not app_ok:
            print("   - App auto-schedule feature issues")

if __name__ == "__main__":
    main()
