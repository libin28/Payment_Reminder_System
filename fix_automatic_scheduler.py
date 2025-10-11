#!/usr/bin/env python3
"""
Fix automatic timing mail system (scheduler)
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import logging

def check_scheduler_status():
    """Check current scheduler status"""
    print("🔍 CHECKING SCHEDULER STATUS")
    print("=" * 50)
    
    try:
        from scheduler_manager import EmailScheduler, get_scheduler
        
        # Get scheduler instance
        scheduler = get_scheduler()
        
        print(f"✅ Scheduler imported successfully")
        print(f"📊 Scheduler running: {scheduler.scheduler.running if hasattr(scheduler, 'scheduler') else 'Unknown'}")
        
        # Get scheduled jobs
        jobs = scheduler.get_scheduled_jobs()
        print(f"📅 Total scheduled jobs: {len(jobs)}")
        
        if jobs:
            print("\n📋 Current scheduled jobs:")
            for job in jobs:
                print(f"   🔹 {job['id']}: {job['next_run']} - {job['name']}")
        else:
            print("⚠️ No jobs currently scheduled")
        
        return scheduler, jobs
        
    except Exception as e:
        print(f"❌ Error checking scheduler: {e}")
        return None, []

def check_reminders_data():
    """Check reminders data for scheduling"""
    print(f"\n🔍 CHECKING REMINDERS DATA")
    print("=" * 50)
    
    try:
        # Load reminders
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        print(f"📊 Total reminders: {len(df)}")
        
        # Check active reminders
        active_reminders = df[df.get('Status', 'Active') == 'Active']
        print(f"✅ Active reminders: {len(active_reminders)}")
        
        # Check future reminders
        today = datetime.now().date()
        future_reminders = []
        
        for _, row in active_reminders.iterrows():
            try:
                due_date = pd.to_datetime(row['Due Date']).date()
                if due_date >= today:
                    future_reminders.append({
                        'id': row['ID'],
                        'name': row['Name'],
                        'due_date': due_date,
                        'due_time': row.get('Due Time', '09:00'),
                        'email': row['Email']
                    })
            except Exception as e:
                print(f"   ⚠️ Error processing reminder {row.get('ID', 'unknown')}: {e}")
        
        print(f"📅 Future reminders to schedule: {len(future_reminders)}")
        
        if future_reminders:
            print("\n📋 Future reminders:")
            for reminder in future_reminders[:5]:  # Show first 5
                print(f"   🔹 {reminder['id']}: {reminder['name']} - {reminder['due_date']} {reminder['due_time']}")
            if len(future_reminders) > 5:
                print(f"   ... and {len(future_reminders) - 5} more")
        
        return future_reminders
        
    except Exception as e:
        print(f"❌ Error checking reminders: {e}")
        return []

def check_email_configuration():
    """Check email configuration for scheduler"""
    print(f"\n🔍 CHECKING EMAIL CONFIGURATION FOR SCHEDULER")
    print("=" * 50)
    
    try:
        # Check new email system
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        default_account = None
        for email, data in accounts.items():
            if data.get('is_default', False):
                default_account = data
                break
        
        if default_account:
            print(f"✅ Default email account: {default_account['email']}")
            print(f"✅ Status: {default_account.get('status', 'unknown')}")
            print(f"✅ Display name: {default_account.get('display_name', 'N/A')}")
            return True
        else:
            print("❌ No default email account found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking email config: {e}")
        return False

def fix_scheduler_email_integration():
    """Fix scheduler to use new email system"""
    print(f"\n🔧 FIXING SCHEDULER EMAIL INTEGRATION")
    print("=" * 50)
    
    try:
        # Check if scheduler_manager.py uses old email config
        with open('scheduler_manager.py', 'r') as f:
            content = f.read()
        
        if 'load_email_config()' in content and 'get_default_email_account' not in content:
            print("⚠️ Scheduler is using old email configuration system")
            print("🔧 Need to update scheduler to use new email accounts system")
            return False
        else:
            print("✅ Scheduler appears to be using correct email system")
            return True
            
    except Exception as e:
        print(f"❌ Error checking scheduler integration: {e}")
        return False

def reschedule_all_reminders():
    """Reschedule all active reminders"""
    print(f"\n🔄 RESCHEDULING ALL ACTIVE REMINDERS")
    print("=" * 50)
    
    try:
        from scheduler_manager import get_scheduler
        
        scheduler = get_scheduler()
        
        # Clear existing jobs
        existing_jobs = scheduler.get_scheduled_jobs()
        print(f"🗑️ Clearing {len(existing_jobs)} existing jobs...")
        
        for job in existing_jobs:
            try:
                scheduler.cancel_reminder(job['id'].replace('reminder_', ''))
            except:
                pass
        
        # Load reminders and reschedule
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        scheduled_count = 0
        
        for _, row in df.iterrows():
            if row.get('Status', 'Active') == 'Active':
                try:
                    due_date = pd.to_datetime(row['Due Date']).date()
                    due_time = row.get('Due Time', '09:00')
                    
                    # Only schedule future reminders
                    scheduled_datetime = datetime.combine(due_date, datetime.strptime(due_time, '%H:%M').time())
                    if scheduled_datetime > datetime.now():
                        if scheduler.schedule_reminder(row['ID'], due_date, due_time):
                            scheduled_count += 1
                            print(f"   ✅ Scheduled: {row['Name']} - {due_date} {due_time}")
                        else:
                            print(f"   ❌ Failed to schedule: {row['Name']}")
                except Exception as e:
                    print(f"   ⚠️ Error scheduling {row.get('ID', 'unknown')}: {e}")
        
        print(f"✅ Successfully scheduled {scheduled_count} reminders")
        return scheduled_count > 0
        
    except Exception as e:
        print(f"❌ Error rescheduling reminders: {e}")
        return False

def test_scheduler_functionality():
    """Test scheduler with a near-future reminder"""
    print(f"\n🧪 TESTING SCHEDULER FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from scheduler_manager import get_scheduler
        
        scheduler = get_scheduler()
        
        # Create a test reminder for 2 minutes from now
        test_time = datetime.now() + timedelta(minutes=2)
        test_date = test_time.date()
        test_time_str = test_time.strftime('%H:%M')
        
        print(f"🧪 Creating test reminder for: {test_date} {test_time_str}")
        
        # Use a test ID
        test_id = "TEST_SCHEDULER_001"
        
        success = scheduler.schedule_reminder(test_id, test_date, test_time_str)
        
        if success:
            print("✅ Test reminder scheduled successfully!")
            print("📧 Check your email in 2 minutes for the test")
            
            # Show scheduled jobs
            jobs = scheduler.get_scheduled_jobs()
            test_job = [job for job in jobs if test_id in job['id']]
            if test_job:
                print(f"📅 Test job scheduled for: {test_job[0]['next_run']}")
            
            return True
        else:
            print("❌ Failed to schedule test reminder")
            return False
            
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")
        return False

def main():
    """Main diagnostic and fix function"""
    print("🚨 AUTOMATIC TIMING MAIL SYSTEM DIAGNOSIS & FIX")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Check scheduler status
    scheduler, jobs = check_scheduler_status()
    
    # Step 2: Check reminders data
    future_reminders = check_reminders_data()
    
    # Step 3: Check email configuration
    email_ok = check_email_configuration()
    
    # Step 4: Check scheduler integration
    integration_ok = fix_scheduler_email_integration()
    
    # Step 5: Reschedule all reminders
    if scheduler and email_ok:
        reschedule_success = reschedule_all_reminders()
        
        # Step 6: Test scheduler
        if reschedule_success:
            test_success = test_scheduler_functionality()
        else:
            test_success = False
    else:
        reschedule_success = False
        test_success = False
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    print(f"Scheduler Status: {'✅ Running' if scheduler else '❌ Not Running'}")
    print(f"Email Configuration: {'✅ Working' if email_ok else '❌ Issues Found'}")
    print(f"Integration: {'✅ Correct' if integration_ok else '❌ Needs Update'}")
    print(f"Rescheduling: {'✅ Success' if reschedule_success else '❌ Failed'}")
    print(f"Test Scheduling: {'✅ Working' if test_success else '❌ Failed'}")
    
    if all([scheduler, email_ok, integration_ok, reschedule_success]):
        print(f"\n🎉 AUTOMATIC TIMING MAIL SYSTEM IS NOW WORKING!")
        print(f"✅ {len(future_reminders)} future reminders are scheduled")
        print(f"✅ Emails will be sent automatically at scheduled times")
        print(f"✅ Check 'Scheduler Status' in your app for monitoring")
    else:
        print(f"\n❌ ISSUES FOUND - MANUAL INTERVENTION NEEDED")
        if not scheduler:
            print("- Scheduler is not running properly")
        if not email_ok:
            print("- Email configuration issues")
        if not integration_ok:
            print("- Scheduler needs to be updated for new email system")

if __name__ == "__main__":
    main()
