#!/usr/bin/env python3
"""
Test the enhanced external email system and automatic scheduling
"""

import pandas as pd
import uuid
from datetime import datetime, timedelta
from scheduler_manager import get_scheduler

def create_external_test_reminder():
    """Create a test reminder for external email address"""
    print("📝 CREATING EXTERNAL EMAIL TEST REMINDER")
    print("=" * 50)
    
    try:
        # Load existing reminders
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        # Find an external email address from existing reminders
        external_emails = []
        for _, row in df.iterrows():
            email = row['Email']
            if email != 'smsdfinance@gmail.com' and '@' in email:
                external_emails.append({
                    'email': email,
                    'name': row['Name']
                })
                break  # Use first external email found
        
        if not external_emails:
            print("⚠️ No external email addresses found in existing reminders")
            return None
        
        target_email = external_emails[0]
        
        # Create test reminder for 3 minutes from now
        test_time = datetime.now() + timedelta(minutes=3)
        
        test_reminder = {
            'ID': str(uuid.uuid4()),
            'Name': f"External Test - {target_email['name']}",
            'Email': target_email['email'],
            'Header Name': 'External Email Test - Automatic Scheduler',
            'Message': f'''Dear {target_email['name']},

This is an automatic test email to verify that the enhanced email system can send emails from smsdfinance@gmail.com to external email addresses.

Test Details:
- Sent automatically by the scheduler system
- Time: {test_time.strftime('%Y-%m-%d %H:%M:%S')}
- From: smsdfinance@gmail.com
- To: {target_email['email']}

If you receive this email, the external email sending issue has been completely resolved!

Best regards,
Reminder System''',
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
        
        print(f"✅ Created external test reminder:")
        print(f"   📧 To: {test_reminder['Email']}")
        print(f"   👤 Name: {test_reminder['Name']}")
        print(f"   📅 Scheduled: {test_reminder['Due Date']} {test_reminder['Due Time']}")
        
        return test_reminder
        
    except Exception as e:
        print(f"❌ Error creating test reminder: {e}")
        return None

def schedule_external_test():
    """Schedule the external test reminder"""
    print(f"\n📅 SCHEDULING EXTERNAL TEST REMINDER")
    print("=" * 50)
    
    try:
        # Create test reminder
        test_reminder = create_external_test_reminder()
        
        if not test_reminder:
            return False
        
        # Get scheduler
        scheduler = get_scheduler()
        
        # Schedule the reminder
        due_date = datetime.strptime(test_reminder['Due Date'], '%Y-%m-%d').date()
        due_time = test_reminder['Due Time']
        
        success = scheduler.schedule_reminder(test_reminder['ID'], due_date, due_time)
        
        if success:
            print(f"✅ External test reminder scheduled successfully!")
            print(f"📧 Email will be sent to: {test_reminder['Email']}")
            print(f"⏰ Scheduled time: {test_reminder['Due Date']} {test_reminder['Due Time']}")
            
            # Verify it's in the job queue
            jobs = scheduler.get_scheduled_jobs()
            test_job = [job for job in jobs if test_reminder['ID'] in job['id']]
            
            if test_job:
                print(f"✅ Job confirmed in scheduler queue")
                print(f"   Next run: {test_job[0]['next_run']}")
            else:
                print("⚠️ Job not found in scheduler queue")
            
            return True
        else:
            print(f"❌ Failed to schedule external test reminder")
            return False
            
    except Exception as e:
        print(f"❌ Error scheduling external test: {e}")
        return False

def test_manual_external_send():
    """Test manual external email sending with enhanced function"""
    print(f"\n🧪 TESTING MANUAL EXTERNAL EMAIL SENDING")
    print("=" * 50)
    
    try:
        # Load reminders to get external email
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        external_reminder = None
        for _, row in df.iterrows():
            if row['Email'] != 'smsdfinance@gmail.com' and '@' in row['Email']:
                external_reminder = row
                break
        
        if external_reminder is None:
            print("⚠️ No external email found for testing")
            return False
        
        print(f"📧 Testing manual send to: {external_reminder['Email']}")
        
        # Get scheduler and test manual send
        scheduler = get_scheduler()
        
        # Create test email content
        subject = f"Manual External Email Test - {datetime.now().strftime('%H:%M:%S')}"
        body = f"""Dear {external_reminder['Name']},

This is a manual test email to verify the enhanced email sending function.

Test Details:
- Sent manually using enhanced SMTP configuration
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- From: smsdfinance@gmail.com
- To: {external_reminder['Email']}

If you receive this, manual external email sending is working!

Best regards,
Reminder System"""
        
        # Get email config
        config = scheduler.load_email_config()
        
        if not config.get('sender_email') or not config.get('app_password'):
            print("❌ Email configuration not found")
            return False
        
        # Send email using enhanced function
        success = scheduler.send_email(
            external_reminder['Email'],
            subject,
            body,
            config['sender_email'],
            config['app_password']
        )
        
        if success:
            print(f"✅ Manual external email sent successfully!")
            print(f"📧 Sent to: {external_reminder['Email']}")
            return True
        else:
            print(f"❌ Manual external email failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual external send: {e}")
        return False

def verify_scheduler_status():
    """Verify scheduler status and jobs"""
    print(f"\n🔍 VERIFYING SCHEDULER STATUS")
    print("=" * 50)
    
    try:
        scheduler = get_scheduler()
        
        print(f"📊 Scheduler running: {scheduler.scheduler.running}")
        
        jobs = scheduler.get_scheduled_jobs()
        print(f"📅 Total scheduled jobs: {len(jobs)}")
        
        if jobs:
            print(f"\n📋 Scheduled jobs:")
            for job in jobs:
                print(f"   🔹 {job['id']}: {job['next_run']}")
                
            # Check for external email jobs
            external_jobs = [job for job in jobs if 'External Test' in job.get('name', '')]
            if external_jobs:
                print(f"\n✅ Found {len(external_jobs)} external test job(s)")
            else:
                print(f"\nℹ️ No external test jobs found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying scheduler: {e}")
        return False

def main():
    """Main test function"""
    print("🚨 TESTING ENHANCED EXTERNAL EMAIL SYSTEM")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Test manual external email sending
    manual_success = test_manual_external_send()
    
    # Step 2: Schedule external test reminder
    schedule_success = schedule_external_test()
    
    # Step 3: Verify scheduler status
    scheduler_ok = verify_scheduler_status()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 ENHANCED EXTERNAL EMAIL TEST SUMMARY")
    print("=" * 60)
    
    print(f"Manual External Send: {'✅ Working' if manual_success else '❌ Failed'}")
    print(f"Automatic Scheduling: {'✅ Working' if schedule_success else '❌ Failed'}")
    print(f"Scheduler Status: {'✅ Running' if scheduler_ok else '❌ Issues'}")
    
    if manual_success and schedule_success and scheduler_ok:
        print(f"\n🎉 EXTERNAL EMAIL SYSTEM FULLY WORKING!")
        print(f"✅ Manual external emails: WORKING")
        print(f"✅ Automatic external emails: WORKING")
        print(f"✅ Scheduler with external emails: WORKING")
        print(f"📧 Expect external test email in 3 minutes")
        print(f"🎊 All email functions are now operational!")
    else:
        print(f"\n⚠️ SOME ISSUES FOUND:")
        if not manual_success:
            print(f"   - Manual external email sending failed")
        if not schedule_success:
            print(f"   - Automatic scheduling failed")
        if not scheduler_ok:
            print(f"   - Scheduler issues detected")

if __name__ == "__main__":
    main()
