#!/usr/bin/env python3
"""
Demonstrate automatic reminder creation and scheduling
"""

import pandas as pd
import uuid
from datetime import datetime, timedelta
from scheduler_manager import get_scheduler, schedule_reminder

def create_demo_automatic_reminder():
    """Create a demo automatic reminder"""
    print("📝 CREATING DEMO AUTOMATIC REMINDER")
    print("=" * 40)
    
    # Create reminder for 5 minutes from now
    send_time = datetime.now() + timedelta(minutes=5)
    
    demo_reminder = {
        'ID': str(uuid.uuid4()),
        'Name': 'Demo User',
        'Email': 'smsdfinance@gmail.com',  # Use working email for demo
        'Header Name': 'Demo: Automatic Email Sending Test',
        'Message': f'''Dear Demo User,

This is a demonstration of the automatic email sending system.

Demo Details:
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Scheduled: {send_time.strftime('%Y-%m-%d %H:%M:%S')}
- System: Automatic Mail Sending
- Purpose: Demonstrate auto-schedule functionality

If you receive this email, it means:
✅ Automatic reminder creation works
✅ Automatic scheduling works  
✅ Automatic email sending works
✅ The system is fully operational

You can now create your own automatic reminders following the same process!

Best regards,
Automatic Mail System''',
        'Due Date': send_time.strftime('%Y-%m-%d'),
        'Due Time': send_time.strftime('%H:%M'),
        'Status': 'Active',
        'Last Sent': '',
        'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"📧 Demo reminder details:")
    print(f"   Name: {demo_reminder['Name']}")
    print(f"   Email: {demo_reminder['Email']}")
    print(f"   Subject: {demo_reminder['Header Name']}")
    print(f"   Due Date: {demo_reminder['Due Date']}")
    print(f"   Due Time: {demo_reminder['Due Time']}")
    
    return demo_reminder

def save_demo_reminder(demo_reminder):
    """Save demo reminder to Excel file"""
    print(f"\n💾 SAVING DEMO REMINDER TO SYSTEM")
    print("=" * 40)
    
    try:
        # Load existing reminders
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        # Add demo reminder
        new_row = pd.DataFrame([demo_reminder])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save to Excel
        with pd.ExcelWriter('payment_reminders.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reminders', index=False)
        
        print(f"✅ Demo reminder saved to Excel file")
        return True
    except Exception as e:
        print(f"❌ Error saving demo reminder: {e}")
        return False

def schedule_demo_reminder(demo_reminder):
    """Schedule the demo reminder (simulating auto-schedule)"""
    print(f"\n📅 SCHEDULING DEMO REMINDER (AUTO-SCHEDULE)")
    print("=" * 40)
    
    try:
        # This simulates what happens when you check "Auto-schedule" in the app
        due_date = datetime.strptime(demo_reminder['Due Date'], '%Y-%m-%d').date()
        due_time = demo_reminder['Due Time']
        
        # Schedule using the same function the app uses
        success = schedule_reminder(demo_reminder['ID'], due_date, due_time)
        
        if success:
            print(f"✅ Demo reminder scheduled successfully!")
            print(f"⏰ Will send automatically at: {demo_reminder['Due Date']} {demo_reminder['Due Time']}")
            
            # Verify in scheduler
            scheduler = get_scheduler()
            jobs = scheduler.get_scheduled_jobs()
            demo_job = [job for job in jobs if demo_reminder['ID'] in job['id']]
            
            if demo_job:
                print(f"✅ Confirmed in scheduler queue")
                print(f"   Job ID: {demo_job[0]['id']}")
                print(f"   Next run: {demo_job[0]['next_run']}")
                return True
            else:
                print("⚠️ Not found in scheduler queue")
                return False
        else:
            print(f"❌ Failed to schedule demo reminder")
            return False
    except Exception as e:
        print(f"❌ Scheduling error: {e}")
        return False

def show_current_scheduled_jobs():
    """Show all currently scheduled jobs"""
    print(f"\n📋 CURRENT SCHEDULED JOBS")
    print("=" * 40)
    
    try:
        scheduler = get_scheduler()
        jobs = scheduler.get_scheduled_jobs()
        
        print(f"📊 Total scheduled jobs: {len(jobs)}")
        
        if jobs:
            print(f"\n📅 Scheduled jobs:")
            for i, job in enumerate(jobs, 1):
                print(f"   {i}. {job['id']}")
                print(f"      Next run: {job['next_run']}")
                print(f"      Name: {job.get('name', 'N/A')}")
                print()
        else:
            print("ℹ️ No jobs currently scheduled")
        
        return len(jobs)
    except Exception as e:
        print(f"❌ Error getting scheduled jobs: {e}")
        return 0

def provide_next_steps():
    """Provide next steps for user"""
    print(f"\n🚀 NEXT STEPS FOR YOU")
    print("=" * 40)
    
    steps = """
NOW YOU CAN CREATE YOUR OWN AUTOMATIC REMINDERS:

1. 🌐 Open your app: http://localhost:8501
2. 🔑 Login as: santhigirifmc@gmail.com
3. ➕ Click "Add Reminder" in sidebar
4. 📝 Fill in the form:
   - Name: Recipient's name
   - Email: Any email address
   - Header Name: Email subject
   - Message: Your message
   - Due Date: Future date
   - Due Time: Exact time
   - Status: Active
   - ✅ Auto-schedule: KEEP CHECKED!
5. 💾 Click "Add Reminder"
6. ✅ Check "Scheduler Status" to verify

🎯 TIPS:
- Always use future dates/times
- Keep "Auto-schedule" checked
- Monitor "Scheduler Status" page
- Check "Manage Reminders" for history

📧 DEMO EMAIL:
- Will be sent in 5 minutes
- Check smsdfinance@gmail.com
- Confirms system is working
"""
    
    print(steps)

def main():
    """Main demo function"""
    print("🎬 AUTOMATIC MAIL SENDING DEMONSTRATION")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Step 1: Create demo reminder
    demo_reminder = create_demo_automatic_reminder()
    
    # Step 2: Save to system
    save_success = save_demo_reminder(demo_reminder)
    
    # Step 3: Schedule automatically
    if save_success:
        schedule_success = schedule_demo_reminder(demo_reminder)
    else:
        schedule_success = False
    
    # Step 4: Show current jobs
    job_count = show_current_scheduled_jobs()
    
    # Step 5: Provide next steps
    provide_next_steps()
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 DEMONSTRATION SUMMARY")
    print("=" * 50)
    
    print(f"Demo Reminder Created: {'✅ Success' if demo_reminder else '❌ Failed'}")
    print(f"Saved to System: {'✅ Success' if save_success else '❌ Failed'}")
    print(f"Auto-Scheduled: {'✅ Success' if schedule_success else '❌ Failed'}")
    print(f"Total Scheduled Jobs: {job_count}")
    
    if save_success and schedule_success:
        print(f"\n🎉 DEMONSTRATION SUCCESSFUL!")
        print(f"✅ Automatic reminder system is working")
        print(f"✅ Demo email will be sent in 5 minutes")
        print(f"✅ You can now create your own automatic reminders")
        print(f"📧 Check smsdfinance@gmail.com for the demo email")
    else:
        print(f"\n⚠️ DEMONSTRATION HAD ISSUES")
        print(f"Please check the errors above")

if __name__ == "__main__":
    main()
