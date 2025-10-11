#!/usr/bin/env python3
"""
Diagnose and fix timing mail system issues
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from scheduler_manager import get_scheduler
import logging

def check_scheduler_detailed():
    """Detailed scheduler check"""
    print("🔍 DETAILED SCHEDULER DIAGNOSIS")
    print("=" * 50)
    
    try:
        scheduler = get_scheduler()
        
        print(f"📊 Scheduler running: {scheduler.scheduler.running}")
        print(f"📊 Scheduler state: {scheduler.scheduler.state}")
        
        # Check jobs
        jobs = scheduler.get_scheduled_jobs()
        print(f"📅 Total scheduled jobs: {len(jobs)}")
        
        if jobs:
            print("\n📋 Detailed job information:")
            for job in jobs:
                print(f"   🔹 Job ID: {job['id']}")
                print(f"      Next run: {job['next_run']}")
                print(f"      Function: {job.get('func', 'N/A')}")
                print(f"      Args: {job.get('args', 'N/A')}")
                print(f"      Trigger: {job.get('trigger', 'N/A')}")
                print()
        
        # Check if scheduler is actually processing jobs
        print("🔍 Checking scheduler job execution...")
        
        return scheduler, len(jobs)
    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        return None, 0

def check_reminders_data():
    """Check reminders data for issues"""
    print(f"\n🔍 CHECKING REMINDERS DATA")
    print("=" * 50)
    
    try:
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        print(f"📊 Total reminders: {len(df)}")
        
        # Check active reminders
        active_reminders = df[df.get('Status', 'Active') == 'Active']
        print(f"✅ Active reminders: {len(active_reminders)}")
        
        # Check future reminders
        now = datetime.now()
        future_reminders = []
        past_reminders = []
        
        for _, row in active_reminders.iterrows():
            try:
                due_date = pd.to_datetime(row['Due Date']).date()
                due_time_str = row.get('Due Time', '09:00')
                due_time = datetime.strptime(due_time_str, '%H:%M').time()
                
                scheduled_datetime = datetime.combine(due_date, due_time)
                
                if scheduled_datetime > now:
                    future_reminders.append({
                        'id': row['ID'],
                        'name': row['Name'],
                        'email': row['Email'],
                        'scheduled_time': scheduled_datetime,
                        'due_date': due_date,
                        'due_time': due_time_str
                    })
                else:
                    past_reminders.append({
                        'id': row['ID'],
                        'name': row['Name'],
                        'scheduled_time': scheduled_datetime
                    })
            except Exception as e:
                print(f"   ⚠️ Error processing reminder {row.get('ID', 'unknown')}: {e}")
        
        print(f"📅 Future reminders: {len(future_reminders)}")
        print(f"⏰ Past reminders: {len(past_reminders)}")
        
        if future_reminders:
            print("\n📋 Future reminders that should be scheduled:")
            for reminder in future_reminders[:5]:
                print(f"   🔹 {reminder['name']}: {reminder['scheduled_time']}")
        
        if past_reminders:
            print(f"\n⚠️ Past reminders (should have been sent):")
            for reminder in past_reminders[:3]:
                print(f"   🔹 {reminder['name']}: {reminder['scheduled_time']}")
        
        return future_reminders, past_reminders
        
    except Exception as e:
        print(f"❌ Error checking reminders: {e}")
        return [], []

def test_manual_scheduler_execution():
    """Test manual execution of scheduler function"""
    print(f"\n🧪 TESTING MANUAL SCHEDULER EXECUTION")
    print("=" * 50)
    
    try:
        scheduler = get_scheduler()
        
        # Load a test reminder
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        if not df.empty:
            test_reminder = df.iloc[0]
            test_id = test_reminder['ID']
            
            print(f"🧪 Testing manual execution with reminder: {test_id}")
            print(f"   Name: {test_reminder['Name']}")
            print(f"   Email: {test_reminder['Email']}")
            
            # Try to manually execute the send function
            result = scheduler.send_reminder_email(test_id)
            
            if result:
                print("✅ Manual execution successful!")
                return True
            else:
                print("❌ Manual execution failed")
                return False
        else:
            print("⚠️ No reminders found for testing")
            return False
            
    except Exception as e:
        print(f"❌ Manual execution error: {e}")
        return False

def check_scheduler_logs():
    """Check scheduler logs for errors"""
    print(f"\n📋 CHECKING SCHEDULER LOGS")
    print("=" * 50)
    
    try:
        # Set up logging to capture scheduler events
        logging.basicConfig(level=logging.DEBUG)
        
        # Check if there are any log files
        import os
        log_files = [f for f in os.listdir('.') if f.endswith('.log')]
        
        if log_files:
            print(f"📄 Found log files: {log_files}")
            # Read recent log entries
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        recent_lines = lines[-10:] if len(lines) > 10 else lines
                        print(f"\n📄 Recent entries from {log_file}:")
                        for line in recent_lines:
                            print(f"   {line.strip()}")
                except:
                    pass
        else:
            print("ℹ️ No log files found")
        
        return True
    except Exception as e:
        print(f"❌ Error checking logs: {e}")
        return False

def fix_scheduler_issues():
    """Fix common scheduler issues"""
    print(f"\n🔧 FIXING SCHEDULER ISSUES")
    print("=" * 50)
    
    try:
        scheduler = get_scheduler()
        
        # Clear all existing jobs
        existing_jobs = scheduler.get_scheduled_jobs()
        print(f"🗑️ Clearing {len(existing_jobs)} existing jobs...")
        
        for job in existing_jobs:
            try:
                scheduler.scheduler.remove_job(job['id'])
            except:
                pass
        
        # Reschedule all active reminders
        print("🔄 Rescheduling all active reminders...")
        scheduler.reschedule_all_active_reminders()
        
        # Check new jobs
        new_jobs = scheduler.get_scheduled_jobs()
        print(f"✅ Rescheduled {len(new_jobs)} jobs")
        
        if new_jobs:
            print("\n📅 New scheduled jobs:")
            for job in new_jobs:
                print(f"   🔹 {job['id']}: {job['next_run']}")
        
        return len(new_jobs) > 0
        
    except Exception as e:
        print(f"❌ Error fixing scheduler: {e}")
        return False

def create_immediate_test():
    """Create a test reminder for immediate execution"""
    print(f"\n🧪 CREATING IMMEDIATE TEST REMINDER")
    print("=" * 50)
    
    try:
        # Create test for 1 minute from now
        test_time = datetime.now() + timedelta(minutes=1)
        
        test_reminder = {
            'ID': f"TEST_{datetime.now().strftime('%H%M%S')}",
            'Name': 'Immediate Test User',
            'Email': 'smsdfinance@gmail.com',
            'Header Name': 'URGENT: Timing System Test',
            'Message': f'''TIMING SYSTEM TEST - {datetime.now().strftime('%H:%M:%S')}

This is an immediate test to verify the timing mail system is working.

Scheduled for: {test_time.strftime('%Y-%m-%d %H:%M:%S')}
Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you receive this email, the timing system is working correctly!''',
            'Due Date': test_time.strftime('%Y-%m-%d'),
            'Due Time': test_time.strftime('%H:%M'),
            'Status': 'Active',
            'Last Sent': '',
            'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to Excel
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        new_row = pd.DataFrame([test_reminder])
        df = pd.concat([df, new_row], ignore_index=True)
        
        with pd.ExcelWriter('payment_reminders.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reminders', index=False)
        
        # Schedule it
        scheduler = get_scheduler()
        due_date = test_time.date()
        due_time = test_time.strftime('%H:%M')
        
        success = scheduler.schedule_reminder(test_reminder['ID'], due_date, due_time)
        
        if success:
            print(f"✅ Immediate test scheduled for: {test_time.strftime('%H:%M:%S')}")
            print(f"📧 Check smsdfinance@gmail.com in 1 minute")
            return True
        else:
            print(f"❌ Failed to schedule immediate test")
            return False
            
    except Exception as e:
        print(f"❌ Error creating immediate test: {e}")
        return False

def main():
    """Main diagnosis and fix function"""
    print("🚨 TIMING MAIL SYSTEM DIAGNOSIS & FIX")
    print("=" * 60)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Check scheduler
    scheduler, job_count = check_scheduler_detailed()
    
    # Step 2: Check reminders data
    future_reminders, past_reminders = check_reminders_data()
    
    # Step 3: Test manual execution
    manual_ok = test_manual_scheduler_execution()
    
    # Step 4: Check logs
    logs_ok = check_scheduler_logs()
    
    # Step 5: Fix scheduler issues
    fix_ok = fix_scheduler_issues()
    
    # Step 6: Create immediate test
    test_ok = create_immediate_test()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 TIMING SYSTEM DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    print(f"Scheduler Status: {'✅ Running' if scheduler else '❌ Not Running'}")
    print(f"Scheduled Jobs: {job_count}")
    print(f"Future Reminders: {len(future_reminders)}")
    print(f"Past Reminders: {len(past_reminders)}")
    print(f"Manual Execution: {'✅ Working' if manual_ok else '❌ Failed'}")
    print(f"Scheduler Fix: {'✅ Applied' if fix_ok else '❌ Failed'}")
    print(f"Immediate Test: {'✅ Created' if test_ok else '❌ Failed'}")
    
    if scheduler and fix_ok and test_ok:
        print(f"\n🎉 TIMING SYSTEM SHOULD NOW BE WORKING!")
        print(f"✅ Scheduler is running and fixed")
        print(f"✅ Reminders have been rescheduled")
        print(f"✅ Immediate test will arrive in 1 minute")
        print(f"📧 Check smsdfinance@gmail.com for test email")
    else:
        print(f"\n❌ TIMING SYSTEM STILL HAS ISSUES")
        print(f"💡 POSSIBLE CAUSES:")
        if not scheduler:
            print(f"   - Scheduler not running properly")
        if not manual_ok:
            print(f"   - Email sending function has issues")
        if not fix_ok:
            print(f"   - Could not reschedule reminders")

if __name__ == "__main__":
    main()
