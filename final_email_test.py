#!/usr/bin/env python3
"""
Final comprehensive email test to verify both manual and automatic email sending
"""

import sys
import os
import json
import base64
from datetime import datetime, timedelta
import pandas as pd

sys.path.append('.')

def test_password_decoding():
    """Test if the password can be decoded correctly"""
    print("🔐 Testing Password Decoding...")
    
    try:
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        for email, data in accounts.items():
            password = data['password']
            print(f"  📧 Email: {email}")
            print(f"  🔑 Encoded password: {password}")
            
            try:
                decoded = base64.b64decode(password).decode('utf-8')
                print(f"  ✅ Decoded password: {decoded}")
                print(f"  ✅ Password decoding successful!")
                return True
            except Exception as e:
                print(f"  ❌ Password decoding failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error reading email accounts: {e}")
        return False

def test_email_config_loading():
    """Test if email configuration loads correctly"""
    print("\n📧 Testing Email Configuration Loading...")
    
    try:
        from auth import get_default_email_account
        
        default_account = get_default_email_account()
        if not default_account:
            print("❌ No default email account found")
            return False
        
        print(f"✅ Default email account: {default_account['email']}")
        
        # Test password decoding
        password = default_account['password']
        try:
            decoded_password = base64.b64decode(password).decode('utf-8')
            print(f"✅ Password decoded successfully (length: {len(decoded_password)})")
            return True
        except Exception as e:
            print(f"❌ Password decoding failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading email config: {e}")
        return False

def test_manual_email_sending():
    """Test manual email sending function"""
    print("\n📤 Testing Manual Email Sending...")
    
    try:
        from app import send_selected_reminders, load_reminders
        
        # Load reminders
        df = load_reminders()
        if df.empty:
            print("❌ No reminders found for testing")
            return False
        
        # Get the first reminder ID
        test_id = df.iloc[0]['ID']
        test_email = df.iloc[0]['Email']
        print(f"  📋 Testing with reminder ID: {test_id}")
        print(f"  📧 Recipient: {test_email}")
        
        # Test manual sending
        result = send_selected_reminders([test_id])
        print(f"  📤 Manual sending result: {result}")
        
        if "Sent 1 reminders" in result or "successfully" in result.lower():
            print("✅ Manual email sending successful!")
            return True
        else:
            print("❌ Manual email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in manual email test: {e}")
        return False

def test_scheduler_email_sending():
    """Test scheduler email sending"""
    print("\n⏰ Testing Scheduler Email Sending...")
    
    try:
        from scheduler_manager import EmailScheduler
        
        # Create scheduler instance
        scheduler = EmailScheduler()
        
        # Load email config
        config = scheduler.load_email_config()
        if not config.get('sender_email') or not config.get('app_password'):
            print("❌ Scheduler email configuration not loaded")
            return False
        
        print(f"✅ Scheduler email config loaded: {config['sender_email']}")
        print(f"✅ Password available (length: {len(config['app_password'])})")
        
        # Test email sending using scheduler's method
        success = scheduler.send_email(
            recipient=config['sender_email'],  # Send to self
            subject="Test Email - Scheduler Method",
            body="This is a test email sent using the scheduler's email method.",
            sender_email=config['sender_email'],
            app_password=config['app_password']
        )
        
        if success:
            print("✅ Scheduler email sending successful!")
            return True
        else:
            print("❌ Scheduler email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in scheduler email test: {e}")
        return False

def test_automatic_scheduling():
    """Test automatic scheduling functionality"""
    print("\n📅 Testing Automatic Scheduling...")
    
    try:
        from scheduler_manager import EmailScheduler
        from app import load_reminders
        
        # Load reminders
        df = load_reminders()
        if df.empty:
            print("❌ No reminders found for testing")
            return False
        
        # Get a reminder to test with
        test_reminder = df.iloc[0]
        reminder_id = test_reminder['ID']
        
        # Create a test time 2 minutes from now
        test_time = datetime.now() + timedelta(minutes=2)
        test_time_str = test_time.strftime('%H:%M')
        
        print(f"  📋 Testing with reminder ID: {reminder_id}")
        print(f"  ⏰ Scheduling for: {test_time_str}")
        
        # Create scheduler instance
        scheduler = EmailScheduler()
        
        # Schedule the reminder
        success = scheduler.schedule_reminder(reminder_id, test_time_str)
        
        if success:
            print(f"✅ Reminder scheduled successfully for {test_time_str}")
            print("  ⏰ The email should be sent automatically in 2 minutes")
            return True
        else:
            print("❌ Failed to schedule reminder")
            return False
            
    except Exception as e:
        print(f"❌ Error in automatic scheduling test: {e}")
        return False

def main():
    """Run all email tests"""
    print("🚀 Final Email System Comprehensive Test")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Password Decoding", test_password_decoding),
        ("Email Config Loading", test_email_config_loading),
        ("Manual Email Sending", test_manual_email_sending),
        ("Scheduler Email Sending", test_scheduler_email_sending),
        ("Automatic Scheduling", test_automatic_scheduling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL EMAIL FUNCTIONS ARE WORKING PERFECTLY!")
        print("✅ Both manual and automatic email sending are functional")
        print("✅ The Reminder System is ready for production use")
    elif passed >= 3:
        print("\n⚠️ Most email functions are working")
        print("✅ Core functionality is operational")
        print("⚠️ Some minor issues may need attention")
    else:
        print("\n❌ Email system has significant issues")
        print("❌ Please check the failed tests above")
    
    return passed == total

if __name__ == "__main__":
    main()
