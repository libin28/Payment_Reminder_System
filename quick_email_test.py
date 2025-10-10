#!/usr/bin/env python3
"""
Quick test to verify email system is working
"""

import sys
import base64
import json

sys.path.append('.')

def test_password_decoding():
    """Test password decoding"""
    print("🔐 Testing Password Decoding...")
    
    try:
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        for email, data in accounts.items():
            password = data['password']
            print(f"  📧 Email: {email}")
            print(f"  🔑 Encoded: {password}")
            
            decoded = base64.b64decode(password).decode('utf-8')
            print(f"  ✅ Decoded: {decoded}")
            return True
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_system_email():
    """Test system email function"""
    print("\n📤 Testing System Email Function...")
    
    try:
        from auth import get_default_email_account
        from app import send_email
        
        # Get email account
        account = get_default_email_account()
        if not account:
            print("  ❌ No email account found")
            return False
        
        print(f"  ✅ Email account: {account['email']}")
        
        # Decode password
        password = account['password']
        decoded_password = base64.b64decode(password).decode('utf-8')
        print(f"  ✅ Password decoded successfully")
        
        # Send test email
        print("  📧 Sending test email...")
        success = send_email(
            recipient=account['email'],  # Send to self
            subject="System Test - Email Working",
            body="This email confirms that both manual and automatic email sending are working correctly.",
            sender_email=account['email'],
            app_password=decoded_password
        )
        
        if success:
            print("  ✅ Email sent successfully!")
            return True
        else:
            print("  ❌ Email sending failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_manual_sending():
    """Test manual sending function"""
    print("\n🎯 Testing Manual Sending Function...")
    
    try:
        from app import send_selected_reminders, load_reminders
        
        # Load reminders
        df = load_reminders()
        if df.empty:
            print("  ❌ No reminders found")
            return False
        
        # Get first reminder
        test_id = df.iloc[0]['ID']
        print(f"  📋 Testing with reminder: {test_id}")
        
        # Send reminder
        result = send_selected_reminders([test_id])
        print(f"  📤 Result: {result}")
        
        if "Sent 1 reminders" in result or "successfully" in result.lower():
            print("  ✅ Manual sending works!")
            return True
        else:
            print("  ❌ Manual sending failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run tests"""
    print("🚀 Quick Email System Test")
    print("=" * 40)
    
    # Test 1: Password decoding
    password_ok = test_password_decoding()
    
    # Test 2: System email function
    system_ok = test_system_email()
    
    # Test 3: Manual sending
    manual_ok = test_manual_sending()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS")
    print("=" * 40)
    
    print(f"Password Decoding: {'✅ PASS' if password_ok else '❌ FAIL'}")
    print(f"System Email Function: {'✅ PASS' if system_ok else '❌ FAIL'}")
    print(f"Manual Sending: {'✅ PASS' if manual_ok else '❌ FAIL'}")
    
    if password_ok and system_ok and manual_ok:
        print("\n🎉 ALL EMAIL FUNCTIONS ARE WORKING!")
        print("✅ Both manual and automatic email sending are now functional")
        print("✅ Your Reminder System is ready for production use")
    else:
        print("\n⚠️ Some issues remain - check the failed tests above")

if __name__ == "__main__":
    main()
