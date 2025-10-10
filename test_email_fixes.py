#!/usr/bin/env python3
"""
Comprehensive test for email fixes - both manual and automatic sending
"""

import sys
import os
import json
import base64
import pandas as pd
from datetime import datetime, timedelta
import uuid

# Add current directory to path
sys.path.append('.')

def test_email_configuration():
    """Test email configuration loading"""
    print("🔍 Testing Email Configuration...")
    
    try:
        from auth import get_default_email_account, load_email_accounts
        
        # Test admin management email loading
        default_account = get_default_email_account()
        if default_account:
            print(f"✅ Default email account found: {default_account['email']}")
            
            # Test password decoding
            password = default_account['password']
            try:
                decoded = base64.b64decode(password).decode('utf-8')
                print(f"✅ Password successfully decoded ({len(decoded)} chars)")
                return True, default_account['email'], decoded
            except Exception as e:
                print(f"❌ Password decoding failed: {e}")
                return False, None, None
        else:
            print("❌ No default email account found")
            return False, None, None
            
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")
        return False, None, None

def test_scheduler_email_config():
    """Test scheduler email configuration loading"""
    print("\n⏰ Testing Scheduler Email Configuration...")
    
    try:
        from scheduler_manager import EmailScheduler
        
        scheduler = EmailScheduler()
        config = scheduler.load_email_config()
        
        if config.get('sender_email') and config.get('app_password'):
            print(f"✅ Scheduler email config loaded: {config['sender_email']}")
            print(f"✅ App password available ({len(config['app_password'])} chars)")
            return True, config
        else:
            print("❌ Scheduler email config incomplete")
            return False, None
            
    except Exception as e:
        print(f"❌ Scheduler email config test failed: {e}")
        return False, None

def test_manual_email_sending():
    """Test manual email sending function"""
    print("\n📧 Testing Manual Email Sending...")
    
    try:
        from app import send_email
        
        # Get email config
        config_ok, email, password = test_email_configuration()
        if not config_ok:
            print("❌ Cannot test manual sending - email config failed")
            return False
        
        # Test email sending
        print(f"📤 Attempting to send test email to {email}...")
        
        success = send_email(
            recipient=email,
            subject="Test Email - Manual Sending Fix",
            body=f"This is a test email sent at {datetime.now()}.\n\nManual email sending is working!",
            sender_email=email,
            app_password=password
        )
        
        if success:
            print("✅ Manual email sending successful!")
            return True
        else:
            print("❌ Manual email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Manual email sending test failed: {e}")
        return False

def test_reminder_data_structure():
    """Test reminder data structure and field names"""
    print("\n📋 Testing Reminder Data Structure...")
    
    try:
        from app import load_reminders
        
        df = load_reminders()
        if df.empty:
            print("⚠️ No reminders found - creating test reminder")
            return create_test_reminder()
        
        print(f"✅ Found {len(df)} reminders")
        print(f"✅ Columns: {list(df.columns)}")
        
        # Check for Header Name column
        if 'Header Name' in df.columns:
            print("✅ 'Header Name' column found")
        elif 'Agreement Name' in df.columns:
            print("⚠️ Found 'Agreement Name' column (old format)")
        else:
            print("❌ Neither 'Header Name' nor 'Agreement Name' column found")
            return False
        
        # Check for required columns
        required_cols = ['ID', 'Name', 'Email', 'Message', 'Due Date', 'Due Time']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing required columns: {missing_cols}")
            return False
        else:
            print("✅ All required columns present")
            return True
            
    except Exception as e:
        print(f"❌ Reminder data structure test failed: {e}")
        return False

def create_test_reminder():
    """Create a test reminder for testing"""
    print("📝 Creating test reminder...")
    
    try:
        from app import save_reminders
        
        # Create test reminder
        test_reminder = {
            'ID': str(uuid.uuid4()),
            'Name': 'Test User',
            'Email': 'liblal2018@gmail.com',  # Use the configured email
            'Header Name': 'Test Reminder',
            'Message': 'This is a test reminder for email functionality testing.',
            'Due Date': datetime.now().date(),
            'Due Time': (datetime.now() + timedelta(minutes=2)).strftime('%H:%M'),
            'Status': 'Active',
            'Last Sent': None
        }
        
        df = pd.DataFrame([test_reminder])
        save_reminders(df)
        
        print(f"✅ Test reminder created with ID: {test_reminder['ID']}")
        print(f"✅ Scheduled for: {test_reminder['Due Time']} today")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test reminder: {e}")
        return False

def test_scheduler_functionality():
    """Test scheduler functionality"""
    print("\n⏰ Testing Scheduler Functionality...")
    
    try:
        from scheduler_manager import EmailScheduler
        from app import load_reminders
        
        scheduler = EmailScheduler()
        df = load_reminders()
        
        if df.empty:
            print("⚠️ No reminders to schedule")
            return False
        
        # Test scheduling a reminder
        test_reminder = df.iloc[0]
        reminder_id = test_reminder['ID']
        
        # Schedule for 1 minute from now
        due_date = datetime.now().date()
        due_time = (datetime.now() + timedelta(minutes=1)).strftime('%H:%M')
        
        print(f"📅 Testing scheduler with reminder {reminder_id}")
        print(f"📅 Scheduled for: {due_time}")
        
        success = scheduler.schedule_reminder(reminder_id, due_date, due_time)
        
        if success:
            print("✅ Scheduler functionality working!")
            return True
        else:
            print("❌ Scheduler functionality failed")
            return False
            
    except Exception as e:
        print(f"❌ Scheduler functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Email System Comprehensive Test")
    print("=" * 50)
    
    tests = [
        ("Email Configuration", test_email_configuration),
        ("Scheduler Email Config", test_scheduler_email_config),
        ("Reminder Data Structure", test_reminder_data_structure),
        ("Manual Email Sending", test_manual_email_sending),
        ("Scheduler Functionality", test_scheduler_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "Email Configuration":
                result = test_func()[0]  # Get boolean result
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Email system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
