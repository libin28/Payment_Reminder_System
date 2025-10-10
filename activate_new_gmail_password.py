#!/usr/bin/env python3
"""
Activate new Gmail app password for smsdfinance@gmail.com
"""

import json
import base64
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def update_gmail_password(new_password):
    """Update Gmail password in the system"""
    
    print(f"🔧 ACTIVATING NEW GMAIL PASSWORD")
    print("=" * 50)
    
    # Clean the password (remove spaces/dashes)
    clean_password = new_password.replace(" ", "").replace("-", "")
    
    print(f"Original password: {new_password}")
    print(f"Cleaned password: {clean_password}")
    print(f"Password length: {len(clean_password)}")
    
    if len(clean_password) != 16:
        print(f"❌ Invalid password length: {len(clean_password)} (should be 16)")
        return False
    
    try:
        # Encode the password
        encoded_password = base64.b64encode(clean_password.encode('utf-8')).decode('utf-8')
        print(f"✅ Password encoded successfully")
        
        # Update email_accounts.json
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        email = 'smsdfinance@gmail.com'
        if email in accounts:
            # Update password and metadata
            accounts[email]['password'] = encoded_password
            accounts[email]['updated_at'] = datetime.now().isoformat()
            accounts[email]['updated_by'] = 'system_activation'
            accounts[email]['status'] = 'active'
            accounts[email]['is_default'] = True
            
            # Save the file
            with open('email_accounts.json', 'w') as f:
                json.dump(accounts, f, indent=4)
            
            print(f"✅ Password updated in email_accounts.json")
            return True, clean_password
        else:
            print(f"❌ Email {email} not found in accounts")
            return False, None
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False, None

def test_new_password(email, password):
    """Test the new password"""
    
    print(f"\n🧪 TESTING NEW PASSWORD")
    print("=" * 50)
    
    try:
        print("1. Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("   ✅ Connected to smtp.gmail.com:587")
        
        print("2. Starting TLS encryption...")
        server.starttls()
        print("   ✅ TLS started")
        
        print("3. Attempting login...")
        server.login(email, password)
        print("   ✅ Login successful!")
        
        print("4. Sending test email...")
        msg = MIMEText(f"Test email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nThis confirms your email system is working!")
        msg['Subject'] = "✅ Email System Activated - Test Successful"
        msg['From'] = email
        msg['To'] = email
        
        server.send_message(msg)
        print("   ✅ Test email sent successfully!")
        
        server.quit()
        print("   ✅ Connection closed")
        
        print(f"\n🎉 SUCCESS! New password is working perfectly!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("   💡 The password is still invalid. Please check:")
        print("      - Password is exactly 16 characters")
        print("      - 2-Step Verification is enabled")
        print("      - App password was generated for 'Mail' category")
        return False
        
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

def main():
    """Main activation function"""
    
    print("🚀 GMAIL PASSWORD ACTIVATION SYSTEM")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Get the new password from user
    print("\n📝 Please enter the NEW 16-character Gmail app password:")
    print("   (The one you just generated from Google Account settings)")
    
    try:
        new_password = input("\nEnter new Gmail app password: ").strip()
        
        if not new_password:
            print("❌ No password entered. Exiting.")
            return
        
        # Update the password
        success, clean_password = update_gmail_password(new_password)
        
        if success:
            # Test the password
            test_success = test_new_password('smsdfinance@gmail.com', clean_password)
            
            if test_success:
                print(f"\n" + "=" * 60)
                print("🎉 EMAIL SYSTEM FULLY ACTIVATED!")
                print("=" * 60)
                print("✅ Password updated in system")
                print("✅ Gmail connection working")
                print("✅ Test email sent successfully")
                print("✅ Manual email sending: READY")
                print("✅ Automatic email sending: READY")
                print("\n🎊 Your email system is now fully operational!")
                
                # Update total sent count
                try:
                    with open('email_accounts.json', 'r') as f:
                        accounts = json.load(f)
                    
                    accounts['smsdfinance@gmail.com']['total_sent'] = accounts['smsdfinance@gmail.com'].get('total_sent', 0) + 1
                    accounts['smsdfinance@gmail.com']['last_used'] = datetime.now().isoformat()
                    
                    with open('email_accounts.json', 'w') as f:
                        json.dump(accounts, f, indent=4)
                    
                    print("✅ Email statistics updated")
                except:
                    pass
                
            else:
                print(f"\n❌ Password updated but still not working.")
                print("💡 Please double-check the Gmail app password and try again.")
        else:
            print(f"\n❌ Failed to update password in system.")
    
    except KeyboardInterrupt:
        print(f"\n\n❌ Operation cancelled.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
