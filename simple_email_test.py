#!/usr/bin/env python3
"""
Simple email test to verify the system is working
"""

import sys
sys.path.append('.')

def test_email_sending():
    """Test email sending directly using the scheduler's method"""
    print("🧪 Testing Email Sending via Scheduler Method...")
    
    try:
        from scheduler_manager import EmailScheduler
        
        # Create scheduler instance
        scheduler = EmailScheduler()
        
        # Load email config using scheduler's method
        config = scheduler.load_email_config()
        
        if not config.get('sender_email') or not config.get('app_password'):
            print("❌ Email configuration not loaded")
            return False
        
        print(f"✅ Email config loaded: {config['sender_email']}")
        print(f"✅ Password length: {len(config['app_password'])} characters")
        
        # Test email sending using scheduler's method
        success = scheduler.send_email(
            recipient=config['sender_email'],  # Send to self
            subject="Test Email - Scheduler Method",
            body="This is a test email sent using the scheduler's email method.",
            sender_email=config['sender_email'],
            app_password=config['app_password']
        )
        
        if success:
            print("✅ Email sent successfully using scheduler method!")
            return True
        else:
            print("❌ Email sending failed using scheduler method")
            return False
            
    except Exception as e:
        print(f"❌ Error in scheduler email test: {e}")
        return False

def test_manual_email_function():
    """Test the manual email sending function from app.py"""
    print("\n🧪 Testing Manual Email Function...")
    
    try:
        from app import send_selected_reminders, load_reminders
        
        # Load reminders to get a test ID
        df = load_reminders()
        if df.empty:
            print("❌ No reminders found for testing")
            return False
        
        # Get the first reminder ID
        test_id = df.iloc[0]['ID']
        print(f"📧 Testing with reminder ID: {test_id}")
        
        # Test manual sending
        result = send_selected_reminders([test_id])
        print(f"📧 Manual sending result: {result}")
        
        if "Sent 1 reminders" in result:
            print("✅ Manual email sending successful!")
            return True
        else:
            print("❌ Manual email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in manual email test: {e}")
        return False

def main():
    """Run email tests"""
    print("🚀 Simple Email System Test")
    print("=" * 40)
    
    # Test 1: Scheduler method
    scheduler_result = test_email_sending()
    
    # Test 2: Manual function
    manual_result = test_manual_email_function()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS")
    print("=" * 40)
    
    print(f"Scheduler Email: {'✅ PASS' if scheduler_result else '❌ FAIL'}")
    print(f"Manual Email: {'✅ PASS' if manual_result else '❌ FAIL'}")
    
    if scheduler_result and manual_result:
        print("\n🎉 All email functions are working!")
    elif scheduler_result:
        print("\n⚠️ Scheduler works, but manual function has issues")
    elif manual_result:
        print("\n⚠️ Manual function works, but scheduler has issues")
    else:
        print("\n❌ Both email functions have issues")
    
    return scheduler_result and manual_result

if __name__ == "__main__":
    main()
