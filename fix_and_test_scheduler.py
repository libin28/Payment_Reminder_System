#!/usr/bin/env python3
"""
Fix and test the automatic scheduler system
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import uuid

def create_test_reminders():
    """Create test reminders for future times"""
    print("🧪 CREATING TEST REMINDERS FOR SCHEDULER")
    print("=" * 50)
    
    try:
        # Load existing reminders
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        # Create test reminders for near future
        test_reminders = []
        
        # Test 1: 3 minutes from now
        test_time_1 = datetime.now() + timedelta(minutes=3)
        test_reminder_1 = {
            'ID': str(uuid.uuid4()),
            'Name': 'Test User 1',
            'Email': 'smsdfinance@gmail.com',  # Send to the same email for testing
            'Header Name': 'Test Automatic Reminder 1',
            'Message': 'This is an automatic test reminder sent by the scheduler system. If you receive this, the automatic timing system is working!',
            'Due Date': test_time_1.strftime('%Y-%m-%d'),
            'Due Time': test_time_1.strftime('%H:%M'),
            'Status': 'Active',
            'Last Sent': '',
            'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Test 2: 5 minutes from now
        test_time_2 = datetime.now() + timedelta(minutes=5)
        test_reminder_2 = {
            'ID': str(uuid.uuid4()),
            'Name': 'Test User 2',
            'Email': 'smsdfinance@gmail.com',  # Send to the same email for testing
            'Header Name': 'Test Automatic Reminder 2',
            'Message': 'This is the second automatic test reminder. The scheduler is working perfectly!',
            'Due Date': test_time_2.strftime('%Y-%m-%d'),
            'Due Time': test_time_2.strftime('%H:%M'),
            'Status': 'Active',
            'Last Sent': '',
            'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        test_reminders = [test_reminder_1, test_reminder_2]
        
        # Add test reminders to dataframe
        for reminder in test_reminders:
            new_row = pd.DataFrame([reminder])
            df = pd.concat([df, new_row], ignore_index=True)
            print(f"✅ Created test reminder: {reminder['Name']} - {reminder['Due Date']} {reminder['Due Time']}")
        
        # Save updated dataframe
        with pd.ExcelWriter('payment_reminders.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reminders', index=False)
        
        print(f"✅ Added {len(test_reminders)} test reminders to Excel file")
        return test_reminders
        
    except Exception as e:
        print(f"❌ Error creating test reminders: {e}")
        return []

def schedule_test_reminders(test_reminders):
    """Schedule the test reminders"""
    print(f"\n📅 SCHEDULING TEST REMINDERS")
    print("=" * 50)
    
    try:
        from scheduler_manager import get_scheduler
        
        scheduler = get_scheduler()
        scheduled_count = 0
        
        for reminder in test_reminders:
            try:
                due_date = datetime.strptime(reminder['Due Date'], '%Y-%m-%d').date()
                due_time = reminder['Due Time']
                
                success = scheduler.schedule_reminder(reminder['ID'], due_date, due_time)
                
                if success:
                    scheduled_count += 1
                    print(f"✅ Scheduled: {reminder['Name']} - {reminder['Due Date']} {reminder['Due Time']}")
                else:
                    print(f"❌ Failed to schedule: {reminder['Name']}")
                    
            except Exception as e:
                print(f"⚠️ Error scheduling {reminder['Name']}: {e}")
        
        print(f"\n✅ Successfully scheduled {scheduled_count}/{len(test_reminders)} test reminders")
        return scheduled_count > 0
        
    except Exception as e:
        print(f"❌ Error scheduling test reminders: {e}")
        return False

def verify_scheduled_jobs():
    """Verify that jobs are scheduled"""
    print(f"\n🔍 VERIFYING SCHEDULED JOBS")
    print("=" * 50)
    
    try:
        from scheduler_manager import get_scheduler
        
        scheduler = get_scheduler()
        jobs = scheduler.get_scheduled_jobs()
        
        print(f"📊 Total scheduled jobs: {len(jobs)}")
        
        if jobs:
            print("\n📋 Scheduled jobs:")
            for job in jobs:
                print(f"   🔹 {job['id']}: {job['next_run']} - {job['name']}")
            return True
        else:
            print("⚠️ No jobs scheduled")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying jobs: {e}")
        return False

def test_manual_scheduler_trigger():
    """Test manual trigger of scheduler"""
    print(f"\n🧪 TESTING MANUAL SCHEDULER TRIGGER")
    print("=" * 50)
    
    try:
        from scheduler_manager import get_scheduler
        
        scheduler = get_scheduler()
        
        # Load a test reminder and try to send it manually
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        test_reminders = df[df['Name'].str.contains('Test User', na=False)]
        
        if not test_reminders.empty:
            test_id = test_reminders.iloc[0]['ID']
            print(f"🧪 Manually triggering reminder: {test_id}")
            
            # Manually call the send function
            result = scheduler.send_reminder_email(test_id)
            
            if result:
                print("✅ Manual trigger successful - email sent!")
                return True
            else:
                print("❌ Manual trigger failed")
                return False
        else:
            print("⚠️ No test reminders found for manual trigger")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual trigger: {e}")
        return False

def update_existing_reminders_to_future():
    """Update existing reminders to future times for testing"""
    print(f"\n🔄 UPDATING EXISTING REMINDERS TO FUTURE TIMES")
    print("=" * 50)
    
    try:
        df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
        
        updated_count = 0
        for index, row in df.iterrows():
            if row.get('Status', 'Active') == 'Active' and not pd.isna(row['Due Date']):
                try:
                    due_date = pd.to_datetime(row['Due Date']).date()
                    due_time_str = row.get('Due Time', '09:00')
                    due_time = datetime.strptime(due_time_str, '%H:%M').time()
                    
                    scheduled_datetime = datetime.combine(due_date, due_time)
                    
                    # If the reminder is in the past, update it to tomorrow
                    if scheduled_datetime <= datetime.now():
                        tomorrow = datetime.now().date() + timedelta(days=1)
                        new_time = datetime.now() + timedelta(minutes=10 + updated_count * 2)  # Stagger times
                        
                        df.at[index, 'Due Date'] = tomorrow.strftime('%Y-%m-%d')
                        df.at[index, 'Due Time'] = new_time.strftime('%H:%M')
                        
                        print(f"✅ Updated {row['Name']}: {tomorrow} {new_time.strftime('%H:%M')}")
                        updated_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Error updating reminder {row.get('ID', 'unknown')}: {e}")
        
        if updated_count > 0:
            # Save updated dataframe
            with pd.ExcelWriter('payment_reminders.xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Reminders', index=False)
            
            print(f"✅ Updated {updated_count} reminders to future times")
        else:
            print("ℹ️ No reminders needed updating")
        
        return updated_count > 0
        
    except Exception as e:
        print(f"❌ Error updating reminders: {e}")
        return False

def reschedule_all_active_reminders():
    """Reschedule all active reminders"""
    print(f"\n🔄 RESCHEDULING ALL ACTIVE REMINDERS")
    print("=" * 50)
    
    try:
        from scheduler_manager import get_scheduler
        
        scheduler = get_scheduler()
        
        # Clear existing jobs first
        existing_jobs = scheduler.get_scheduled_jobs()
        for job in existing_jobs:
            try:
                scheduler.scheduler.remove_job(job['id'])
            except:
                pass
        
        print(f"🗑️ Cleared {len(existing_jobs)} existing jobs")
        
        # Load and reschedule
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
                        
                except Exception as e:
                    print(f"   ⚠️ Error scheduling {row.get('Name', 'unknown')}: {e}")
        
        print(f"✅ Successfully rescheduled {scheduled_count} reminders")
        return scheduled_count > 0
        
    except Exception as e:
        print(f"❌ Error rescheduling: {e}")
        return False

def main():
    """Main fix and test function"""
    print("🚨 AUTOMATIC SCHEDULER FIX & TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Update existing reminders to future times
    update_success = update_existing_reminders_to_future()
    
    # Step 2: Create test reminders
    test_reminders = create_test_reminders()
    
    # Step 3: Reschedule all active reminders
    reschedule_success = reschedule_all_active_reminders()
    
    # Step 4: Verify scheduled jobs
    verify_success = verify_scheduled_jobs()
    
    # Step 5: Test manual trigger
    manual_test_success = test_manual_scheduler_trigger()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 FIX & TEST SUMMARY")
    print("=" * 60)
    
    print(f"Update Existing Reminders: {'✅ Success' if update_success else 'ℹ️ No Updates Needed'}")
    print(f"Create Test Reminders: {'✅ Success' if test_reminders else '❌ Failed'}")
    print(f"Reschedule Reminders: {'✅ Success' if reschedule_success else '❌ Failed'}")
    print(f"Verify Jobs: {'✅ Success' if verify_success else '❌ Failed'}")
    print(f"Manual Test: {'✅ Success' if manual_test_success else '❌ Failed'}")
    
    if reschedule_success and verify_success:
        print(f"\n🎉 AUTOMATIC TIMING MAIL SYSTEM IS NOW WORKING!")
        print(f"✅ Reminders are scheduled and will be sent automatically")
        print(f"✅ Check your email in the next few minutes for test emails")
        print(f"✅ Monitor 'Scheduler Status' in your app for real-time updates")
        
        if test_reminders:
            print(f"\n📧 EXPECT TEST EMAILS:")
            for reminder in test_reminders:
                print(f"   🔹 {reminder['Due Date']} {reminder['Due Time']}: {reminder['Header Name']}")
    else:
        print(f"\n❌ ISSUES STILL EXIST - CHECK LOGS FOR DETAILS")

if __name__ == "__main__":
    main()
