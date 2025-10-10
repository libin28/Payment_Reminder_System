#!/usr/bin/env python3
"""
Emergency email fix - comprehensive diagnosis and repair
"""

import json
import base64
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def check_email_configuration():
    """Check current email configuration"""
    print("🔍 CHECKING EMAIL CONFIGURATION")
    print("=" * 50)
    
    try:
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        print(f"📧 Total email accounts: {len(accounts)}")
        
        for email, data in accounts.items():
            print(f"\n📧 Email: {email}")
            print(f"   Display Name: {data.get('display_name', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Is Default: {data.get('is_default', False)}")
            print(f"   Total Sent: {data.get('total_sent', 0)}")
            
            # Check password
            try:
                encoded_password = data.get('password', '')
                decoded_password = base64.b64decode(encoded_password).decode('utf-8')
                print(f"   Password Length: {len(decoded_password)} chars")
                print(f"   Password Format: {'✅ Valid' if len(decoded_password) == 16 else '❌ Invalid'}")
            except Exception as e:
                print(f"   Password Error: {e}")
        
        return accounts
        
    except Exception as e:
        print(f"❌ Error reading email accounts: {e}")
        return {}

def test_smtp_connection(email, password):
    """Test SMTP connection with detailed logging"""
    print(f"\n🧪 TESTING SMTP CONNECTION FOR: {email}")
    print("-" * 50)
    
    try:
        print("Step 1: Creating SMTP connection...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("✅ Connected to smtp.gmail.com:587")
        
        print("Step 2: Starting TLS...")
        server.starttls()
        print("✅ TLS started")
        
        print("Step 3: Attempting login...")
        server.login(email, password)
        print("✅ Login successful!")
        
        print("Step 4: Closing connection...")
        server.quit()
        print("✅ Connection closed")
        
        return True, "Connection successful"
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = str(e)
        print(f"❌ Authentication failed: {error_msg}")
        return False, f"Authentication error: {error_msg}"
        
    except smtplib.SMTPConnectError as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        return False, f"Connection error: {error_msg}"
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error: {error_msg}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False, f"Error: {error_msg}"

def send_test_email(email, password, test_recipient="test@example.com"):
    """Send a test email"""
    print(f"\n📧 SENDING TEST EMAIL FROM: {email}")
    print("-" * 50)
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email  # Send to self for testing
        msg['Subject'] = f"Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
        This is a test email from the Reminder System.
        
        Sent from: {email}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        If you receive this email, the email configuration is working correctly!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        print("Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("Logging in...")
        server.login(email, password)
        
        print("Sending email...")
        text = msg.as_string()
        server.sendmail(email, email, text)
        
        print("Closing connection...")
        server.quit()
        
        print("✅ Test email sent successfully!")
        return True, "Test email sent"
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed to send test email: {error_msg}")
        return False, f"Send error: {error_msg}"

def check_app_email_functions():
    """Check if the app's email functions are working"""
    print(f"\n🔧 CHECKING APP EMAIL FUNCTIONS")
    print("-" * 50)
    
    try:
        # Import app modules
        from auth import get_default_email_account, load_email_accounts
        
        print("✅ Successfully imported email functions")
        
        # Check default email account
        default_account = get_default_email_account()
        if default_account:
            print(f"✅ Default email account found: {default_account.get('email', 'N/A')}")
            return default_account
        else:
            print("❌ No default email account found")
            
            # Check all accounts
            all_accounts = load_email_accounts()
            print(f"📊 Total accounts in system: {len(all_accounts)}")
            
            for email, data in all_accounts.items():
                print(f"   - {email}: default={data.get('is_default', False)}")
            
            return None
            
    except Exception as e:
        print(f"❌ Error checking app functions: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def fix_default_email():
    """Fix default email configuration"""
    print(f"\n🔧 FIXING DEFAULT EMAIL CONFIGURATION")
    print("-" * 50)
    
    try:
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        # Find smsdfinance@gmail.com and set as default
        target_email = 'smsdfinance@gmail.com'
        
        if target_email in accounts:
            # Set all accounts to not default
            for email in accounts:
                accounts[email]['is_default'] = False
            
            # Set target as default
            accounts[target_email]['is_default'] = True
            accounts[target_email]['status'] = 'active'
            
            # Save changes
            with open('email_accounts.json', 'w') as f:
                json.dump(accounts, f, indent=4)
            
            print(f"✅ Set {target_email} as default email account")
            return True
        else:
            print(f"❌ {target_email} not found in accounts")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing default email: {e}")
        return False

def main():
    """Main diagnostic and fix function"""
    print("🚨 EMERGENCY EMAIL SYSTEM DIAGNOSIS & FIX")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Check email configuration
    accounts = check_email_configuration()
    
    if not accounts:
        print("\n❌ CRITICAL: No email accounts found!")
        return
    
    # Step 2: Check app functions
    default_account = check_app_email_functions()
    
    # Step 3: Fix default email if needed
    if not default_account:
        print("\n🔧 Attempting to fix default email...")
        fix_default_email()
        
        # Re-check
        default_account = check_app_email_functions()
    
    # Step 4: Test email connection
    if default_account:
        email = default_account.get('email')
        try:
            encoded_password = default_account.get('password', '')
            password = base64.b64decode(encoded_password).decode('utf-8')
            
            # Test connection
            conn_success, conn_msg = test_smtp_connection(email, password)
            
            if conn_success:
                # Test sending
                send_success, send_msg = send_test_email(email, password)
                
                if send_success:
                    print(f"\n🎉 SUCCESS! Email system is working!")
                    print(f"✅ Connection: Working")
                    print(f"✅ Sending: Working")
                    print(f"✅ Default Account: {email}")
                else:
                    print(f"\n⚠️ Connection works but sending failed: {send_msg}")
            else:
                print(f"\n❌ Connection failed: {conn_msg}")
                print("\n💡 SOLUTION NEEDED:")
                print("1. Generate new Gmail app password")
                print("2. Update password in Email Management")
                print("3. Ensure 2-Step Verification is enabled")
        
        except Exception as e:
            print(f"\n❌ Error testing default account: {e}")
    
    else:
        print(f"\n❌ CRITICAL: No default email account configured!")
        print("\n💡 SOLUTION:")
        print("1. Login to your system")
        print("2. Go to Admin Management → Email Management")
        print("3. Set smsdfinance@gmail.com as default")
    
    print(f"\n" + "=" * 60)
    print("🏁 DIAGNOSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
