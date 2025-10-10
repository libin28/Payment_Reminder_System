#!/usr/bin/env python3
"""
Test Gmail connection and fix email sending issues
"""

import smtplib
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_connection():
    """Test Gmail SMTP connection with current credentials"""
    print("🔍 Testing Gmail Connection...")
    
    # Load credentials from email_config.json (fallback)
    try:
        with open('email_config.json', 'r') as f:
            config = json.load(f)
        
        sender_email = config['sender_email']
        app_password = config['app_password']
        
        print(f"📧 Email: {sender_email}")
        print(f"🔑 Password: {app_password}")
        
    except Exception as e:
        print(f"❌ Error loading email config: {e}")
        return False
    
    # Test SMTP connection
    try:
        print("🔌 Connecting to Gmail SMTP...")
        
        # Create SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Attempting login...")
        server.login(sender_email, app_password)
        
        print("✅ Gmail connection successful!")
        
        # Send test email
        print("📤 Sending test email...")
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email  # Send to self
        msg['Subject'] = "Test Email - Connection Verification"
        
        body = "This is a test email to verify Gmail connection is working."
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("🔧 This means the app password is invalid or expired")
        return False
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def generate_new_app_password_instructions():
    """Provide instructions for generating new Gmail app password"""
    print("\n" + "="*60)
    print("🔧 HOW TO FIX GMAIL AUTHENTICATION")
    print("="*60)
    
    print("\n📋 Step 1: Generate New Gmail App Password")
    print("   1. Go to: https://myaccount.google.com/")
    print("   2. Click 'Security' in the left menu")
    print("   3. Under 'Signing in to Google', click '2-Step Verification'")
    print("   4. Scroll down and click 'App passwords'")
    print("   5. Select 'Mail' as the app")
    print("   6. Select 'Windows Computer' as the device")
    print("   7. Click 'Generate'")
    print("   8. Copy the 16-character password (format: abcd efgh ijkl mnop)")
    
    print("\n📋 Step 2: Update Password in System")
    print("   Option A - Via Web Interface (Recommended):")
    print("   1. Go to: http://localhost:8501")
    print("   2. Login as admin: admin@reminder.com / Admin@123")
    print("   3. Go to 'Admin Management' → 'Email Management'")
    print("   4. Edit the email account")
    print("   5. Update the password with new app password")
    print("   6. Click 'Update Account'")
    
    print("\n   Option B - Direct File Update:")
    print("   1. Update email_config.json with new password")
    print("   2. Run the password update script")

def update_password_directly():
    """Allow direct password update for testing"""
    print("\n🔧 Direct Password Update")
    print("Enter the new Gmail app password (or press Enter to skip):")
    
    try:
        new_password = input("New password: ").strip()
        
        if not new_password:
            print("Skipping password update")
            return False
        
        # Update email_config.json
        config = {
            "sender_email": "liblal2018@gmail.com",
            "app_password": new_password
        }
        
        with open('email_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update email_accounts.json with base64 encoded password
        encoded_password = base64.b64encode(new_password.encode('utf-8')).decode('utf-8')
        
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        for email, data in accounts.items():
            if email == 'liblal2018@gmail.com':
                data['password'] = encoded_password
                data['updated_at'] = "2025-10-09T14:00:00.000000"
        
        with open('email_accounts.json', 'w') as f:
            json.dump(accounts, f, indent=2)
        
        print("✅ Password updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False

def test_system_email_functions():
    """Test the system's email functions"""
    print("\n🧪 Testing System Email Functions...")
    
    try:
        import sys
        sys.path.append('.')
        
        from app import send_email
        from auth import get_default_email_account
        
        # Test email config loading
        default_account = get_default_email_account()
        if not default_account:
            print("❌ No default email account found")
            return False
        
        print(f"✅ Default email account loaded: {default_account['email']}")
        
        # Test password decoding
        password = default_account['password']
        try:
            decoded_password = base64.b64decode(password).decode('utf-8')
            print(f"✅ Password decoded successfully")
        except Exception as e:
            print(f"❌ Password decoding failed: {e}")
            return False
        
        # Test email sending function
        print("📤 Testing email sending function...")
        
        success = send_email(
            recipient=default_account['email'],  # Send to self
            subject="System Test Email",
            body="This is a test email from the reminder system.",
            sender_email=default_account['email'],
            app_password=decoded_password
        )
        
        if success:
            print("✅ System email function working!")
            return True
        else:
            print("❌ System email function failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing system functions: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Gmail Connection and Email System Test")
    print("="*50)
    
    # Test 1: Gmail connection
    gmail_works = test_gmail_connection()
    
    if not gmail_works:
        generate_new_app_password_instructions()
        
        # Offer direct password update
        if update_password_directly():
            print("\n🔄 Retesting with new password...")
            gmail_works = test_gmail_connection()
    
    # Test 2: System functions
    if gmail_works:
        print("\n" + "="*50)
        system_works = test_system_email_functions()
        
        if system_works:
            print("\n🎉 ALL EMAIL FUNCTIONS ARE WORKING!")
            print("✅ Both manual and automatic email sending should work now")
        else:
            print("\n⚠️ Gmail works but system functions have issues")
    
    else:
        print("\n❌ Gmail authentication is still failing")
        print("Please follow the instructions above to generate a new app password")

if __name__ == "__main__":
    main()
