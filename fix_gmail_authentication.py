#!/usr/bin/env python3
"""
Fix Gmail authentication issues for smsdfinance@gmail.com
"""

import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_connection(email, password):
    """Test Gmail SMTP connection with detailed error reporting"""
    print(f"🧪 Testing Gmail connection for: {email}")
    print("=" * 50)
    
    try:
        print("1. Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("   ✅ Connected to smtp.gmail.com:587")
        
        print("2. Starting TLS encryption...")
        server.starttls()
        print("   ✅ TLS encryption started")
        
        print("3. Attempting login...")
        server.login(email, password)
        print("   ✅ Login successful!")
        
        server.quit()
        print("   ✅ Connection closed properly")
        
        return True, "Connection successful"
        
    except smtplib.SMTPAuthenticationError as e:
        error_code = str(e.smtp_code) if hasattr(e, 'smtp_code') else 'Unknown'
        error_msg = str(e.smtp_error) if hasattr(e, 'smtp_error') else str(e)
        
        print(f"   ❌ Authentication failed (Code: {error_code})")
        print(f"   📝 Error: {error_msg}")
        
        return False, f"Authentication failed: {error_msg}"
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False, f"Connection failed: {e}"

def check_current_password():
    """Check the current password in email_accounts.json"""
    try:
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        email = 'smsdfinance@gmail.com'
        if email in accounts:
            encoded_password = accounts[email]['password']
            decoded_password = base64.b64decode(encoded_password).decode('utf-8')
            
            print(f"📧 Email: {email}")
            print(f"🔒 Current password: {decoded_password}")
            print(f"📏 Password length: {len(decoded_password)} characters")
            print(f"✅ Expected length: 16 characters (Gmail app password)")
            
            return email, decoded_password
        else:
            print(f"❌ Email {email} not found in accounts")
            return None, None
            
    except Exception as e:
        print(f"❌ Error reading email accounts: {e}")
        return None, None

def update_gmail_password(email, new_password):
    """Update Gmail password in email_accounts.json"""
    try:
        # Validate password format
        clean_password = new_password.replace(' ', '').replace('-', '')
        
        if len(clean_password) != 16:
            print(f"❌ Invalid password length: {len(clean_password)} (should be 16)")
            return False
        
        # Encode the password
        encoded_password = base64.b64encode(clean_password.encode('utf-8')).decode('utf-8')
        
        # Update the file
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        if email in accounts:
            accounts[email]['password'] = encoded_password
            
            with open('email_accounts.json', 'w') as f:
                json.dump(accounts, f, indent=4)
            
            print(f"✅ Password updated for {email}")
            return True
        else:
            print(f"❌ Email {email} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False

def main():
    """Main function to diagnose and fix Gmail authentication"""
    print("🔧 GMAIL AUTHENTICATION TROUBLESHOOTER")
    print("=" * 60)
    
    # Check current configuration
    print("\n📋 STEP 1: Checking Current Configuration")
    print("-" * 40)
    email, current_password = check_current_password()
    
    if not email or not current_password:
        print("❌ Cannot proceed - email configuration not found")
        return
    
    # Test current password
    print(f"\n🧪 STEP 2: Testing Current Password")
    print("-" * 40)
    success, message = test_gmail_connection(email, current_password)
    
    if success:
        print("🎉 Current password works! No changes needed.")
        return
    
    # Provide solution steps
    print(f"\n💡 STEP 3: Solution Required")
    print("-" * 40)
    print("❌ Current Gmail app password is not working.")
    print("\n📝 TO FIX THIS ISSUE:")
    print("\n1️⃣ Generate New Gmail App Password:")
    print("   • Go to: https://myaccount.google.com/")
    print("   • Login as: smsdfinance@gmail.com")
    print("   • Go to: Security → 2-Step Verification → App passwords")
    print("   • Create new password for 'Mail' application")
    print("   • Copy the 16-character password (e.g., 'abcdwxyzpqrs1234')")
    
    print("\n2️⃣ Update Password in System:")
    print("   • Login to: http://localhost:8501")
    print("   • Login as: santhigirifmc@gmail.com")
    print("   • Go to: Admin Management → Email Management → Manage Accounts")
    print("   • Select: smsdfinance@gmail.com")
    print("   • Update: Enter new 16-character app password")
    print("   • Test: Use 'Test Connection' button")
    
    print("\n3️⃣ Alternative - Update via Script:")
    print("   • Run this script again with: python fix_gmail_authentication.py")
    print("   • When prompted, enter the new 16-character app password")
    
    # Ask if user wants to update password now
    print(f"\n🔄 STEP 4: Update Password Now (Optional)")
    print("-" * 40)
    print("If you have a new Gmail app password, you can update it now:")
    
    try:
        user_input = input("\nDo you have a new Gmail app password to test? (y/n): ").lower().strip()
        
        if user_input == 'y':
            new_password = input("Enter the new 16-character Gmail app password: ").strip()
            
            if update_gmail_password(email, new_password):
                print("\n🧪 Testing new password...")
                success, message = test_gmail_connection(email, new_password.replace(' ', '').replace('-', ''))
                
                if success:
                    print("🎉 SUCCESS! New password works perfectly!")
                    print("✅ Email sending should now work properly.")
                else:
                    print(f"❌ New password still not working: {message}")
                    print("💡 Please double-check the app password and try again.")
            else:
                print("❌ Failed to update password")
        else:
            print("📝 Please follow the steps above to generate a new Gmail app password.")
            
    except KeyboardInterrupt:
        print("\n\n📝 Please follow the manual steps above to fix the Gmail authentication.")
    except Exception as e:
        print(f"\n❌ Error during password update: {e}")

if __name__ == "__main__":
    main()
