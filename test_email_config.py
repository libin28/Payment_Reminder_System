#!/usr/bin/env python3
"""
Test Email Configuration
Check email account setup and test sending functionality
"""

import sys
import base64
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_email_configuration():
    """Test email account configuration"""
    print("🔍 Testing Email Configuration")
    print("=" * 50)
    
    try:
        from auth import get_default_email_account, load_email_accounts
        
        # Check email accounts
        accounts = load_email_accounts()
        print(f"📧 Total email accounts: {len(accounts)}")
        
        if not accounts:
            print("❌ No email accounts configured!")
            print("   Please add an email account in Admin Management → Email Management")
            return False
        
        # Show account details
        for email, data in accounts.items():
            print(f"\n📧 Email: {email}")
            print(f"   Display Name: {data.get('display_name', 'N/A')}")
            print(f"   Is Default: {data.get('is_default', False)}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Total Sent: {data.get('total_sent', 0)}")
            
            # Check password
            try:
                password = data.get('password', '')
                if password:
                    decoded_password = base64.b64decode(password).decode('utf-8')
                    print(f"   Password: {'*' * len(decoded_password)} ({len(decoded_password)} chars)")
                else:
                    print("   Password: Not set")
            except Exception as e:
                print(f"   Password: Invalid encoding - {e}")
        
        # Check default account
        print(f"\n🎯 Default Email Account:")
        default = get_default_email_account()
        if default:
            print(f"   Email: {default['email']}")
            print(f"   Password Length: {len(default['password'])} characters")
            return True
        else:
            print("   ❌ No default email account set!")
            print("   Please set a default email account in Admin Management")
            return False
            
    except Exception as e:
        print(f"❌ Error checking email configuration: {e}")
        return False

def test_email_sending():
    """Test email sending functionality"""
    print("\n📤 Testing Email Sending")
    print("=" * 30)
    
    try:
        from auth import get_default_email_account
        from app import send_email
        
        # Get default account
        default_account = get_default_email_account()
        if not default_account:
            print("❌ No default email account configured")
            return False
        
        # Test email sending (to the same email address to avoid spam)
        test_recipient = default_account['email']  # Send to self
        test_subject = "Test Email from Reminder System"
        test_body = f"This is a test email sent at {datetime.now()}\n\nIf you receive this, email sending is working correctly!"
        
        print(f"📧 Sending test email to: {test_recipient}")
        print(f"📧 From: {default_account['email']}")
        
        success = send_email(
            recipient=test_recipient,
            subject=test_subject,
            body=test_body,
            sender_email=default_account['email'],
            app_password=default_account['password']
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print("   Check your inbox to confirm delivery")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email sending: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler_integration():
    """Test scheduler email integration"""
    print("\n⏰ Testing Scheduler Integration")
    print("=" * 35)
    
    try:
        from scheduler_manager import EmailScheduler
        
        # Create scheduler instance
        scheduler = EmailScheduler()
        
        # Test email config loading
        config = scheduler.load_email_config()
        if config.get('sender_email') and config.get('app_password'):
            print(f"✅ Scheduler can load email config")
            print(f"   Email: {config['sender_email']}")
            print(f"   Password: {'*' * len(config['app_password'])}")
            return True
        else:
            print("❌ Scheduler cannot load email config")
            print("   This will prevent automatic email sending")
            return False
            
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")
        return False

def check_reminders_data():
    """Check if there are any reminders to send"""
    print("\n📋 Checking Reminders Data")
    print("=" * 30)
    
    try:
        from app import load_reminders
        import pandas as pd
        
        df = load_reminders()
        if df.empty:
            print("📭 No reminders found")
            print("   Add some reminders to test email sending")
            return False
        
        print(f"📋 Found {len(df)} reminders")
        
        # Check for today's reminders
        today = datetime.today().date()
        today_reminders = 0
        
        for _, row in df.iterrows():
            if pd.notna(row['Due Date']):
                due_date = pd.to_datetime(row['Due Date']).date()
                if due_date == today and row.get('Status', 'Active') == 'Active':
                    today_reminders += 1
        
        print(f"📅 Reminders due today: {today_reminders}")
        
        # Show sample reminder
        if len(df) > 0:
            sample = df.iloc[0]
            print(f"\n📝 Sample reminder:")
            print(f"   Name: {sample.get('Name', 'N/A')}")
            print(f"   Email: {sample.get('Email', 'N/A')}")
            print(f"   Header: {sample.get('Header Name', 'N/A')}")
            print(f"   Due Date: {sample.get('Due Date', 'N/A')}")
            print(f"   Status: {sample.get('Status', 'Active')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking reminders: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Email System Diagnostic Test")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Email Configuration", test_email_configuration),
        ("Email Sending", test_email_sending),
        ("Scheduler Integration", test_scheduler_integration),
        ("Reminders Data", check_reminders_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Email system should be working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Add a valid email account in Admin Management → Email Management")
        print("2. Set a default email account")
        print("3. Use a valid Gmail app password (not regular password)")
        print("4. Ensure email account status is 'active'")
