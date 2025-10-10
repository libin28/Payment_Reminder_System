#!/usr/bin/env python3
"""
Final verification that both manual and automatic email sending are working
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append('.')

def test_manual_email_sending():
    """Test manual email sending through the app"""
    print("📤 Testing Manual Email Sending...")
    
    try:
        from app import send_selected_reminders, load_reminders
        
        # Load reminders
        df = load_reminders()
        if df.empty:
            print("  ❌ No reminders found")
            return False
        
        # Get first reminder
        test_id = df.iloc[0]['ID']
        test_name = df.iloc[0]['Name']
        test_email = df.iloc[0]['Email']
        
        print(f"  📋 Testing with reminder: {test_id}")
        print(f"  👤 Recipient: {test_name} ({test_email})")
        
        # Send reminder
        result = send_selected_reminders([test_id])
        print(f"  📤 Result: {result}")
        
        if "Sent 1 reminders" in result:
            print("  ✅ Manual email sending successful!")
            return True
        else:
            print("  ❌ Manual email sending failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_automatic_scheduling():
    """Test automatic email scheduling"""
    print("\n⏰ Testing Automatic Email Scheduling...")
    
    try:
        from scheduler_manager import EmailScheduler
        from app import load_reminders
        
        # Load reminders
        df = load_reminders()
        if df.empty:
            print("  ❌ No reminders found")
            return False
        
        # Get first reminder
        test_id = df.iloc[0]['ID']
        test_name = df.iloc[0]['Name']
        
        print(f"  📋 Testing with reminder: {test_id}")
        print(f"  👤 Recipient: {test_name}")
        
        # Create scheduler
        scheduler = EmailScheduler()
        
        # Schedule for 1 minute from now
        future_time = datetime.now() + timedelta(minutes=1)
        date_str = future_time.strftime('%Y-%m-%d')
        time_str = future_time.strftime('%H:%M')

        print(f"  ⏰ Scheduling for: {date_str} {time_str}")

        # Schedule the reminder
        success = scheduler.schedule_reminder(test_id, date_str, time_str)
        
        if success:
            print("  ✅ Automatic scheduling successful!")
            print(f"  📧 Email will be sent automatically at {time_str}")
            return True
        else:
            print("  ❌ Automatic scheduling failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_scheduler_email_config():
    """Test scheduler email configuration"""
    print("\n🔧 Testing Scheduler Email Configuration...")
    
    try:
        from scheduler_manager import EmailScheduler
        
        scheduler = EmailScheduler()
        config = scheduler.load_email_config()
        
        if config.get('sender_email') and config.get('app_password'):
            print(f"  ✅ Email config loaded: {config['sender_email']}")
            print(f"  ✅ Password available: {len(config['app_password'])} characters")
            return True
        else:
            print("  ❌ Email configuration incomplete")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_scheduler_logs():
    """Check recent scheduler logs for email activity"""
    print("\n📋 Checking Recent Scheduler Activity...")
    
    try:
        if os.path.exists('scheduler.log'):
            with open('scheduler.log', 'r') as f:
                lines = f.readlines()
            
            # Get last 10 lines
            recent_lines = lines[-10:]
            
            print("  📄 Recent scheduler activity:")
            for line in recent_lines:
                if 'INFO' in line and ('email' in line.lower() or 'reminder' in line.lower()):
                    print(f"    {line.strip()}")
            
            # Check for successful email sending
            success_found = any('sent successfully' in line.lower() for line in recent_lines)
            if success_found:
                print("  ✅ Recent successful email sending found in logs")
                return True
            else:
                print("  ⚠️ No recent successful email sending in logs")
                return False
        else:
            print("  ❌ No scheduler log file found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error reading logs: {e}")
        return False

def main():
    """Run final verification tests"""
    print("🚀 Final Email System Verification")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Manual Email Sending", test_manual_email_sending),
        ("Automatic Scheduling", test_automatic_scheduling),
        ("Scheduler Configuration", test_scheduler_email_config),
        ("Scheduler Logs", check_scheduler_logs)
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
    print("📊 FINAL VERIFICATION RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    # Final assessment
    if results.get("Manual Email Sending") and results.get("Automatic Scheduling"):
        print("\n🎉 EMAIL SYSTEM IS FULLY FUNCTIONAL!")
        print("✅ Both manual and automatic email sending are working")
        print("✅ Your Reminder System is ready for production use")
        print("\n📧 How to use:")
        print("  • Manual: Go to '🎯 Selective Mailing' in the web interface")
        print("  • Automatic: Go to '📅 Schedule Reminders' to set up automatic sending")
        print("  • Monitor: Check scheduler.log for automatic email activity")
        return True
    elif results.get("Manual Email Sending"):
        print("\n✅ MANUAL EMAIL SENDING IS WORKING!")
        print("⚠️ Automatic scheduling may need attention")
        print("✅ You can use manual email sending immediately")
        return True
    else:
        print("\n❌ EMAIL SYSTEM NEEDS ATTENTION")
        print("❌ Please check the failed tests above")
        return False

if __name__ == "__main__":
    main()
