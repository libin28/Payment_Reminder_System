#!/usr/bin/env python3
"""
Verify admin permissions and email configuration fixes
"""

import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_admin_permissions():
    """Check if santhigirifmc@gmail.com has proper admin permissions"""
    print("🔍 Checking Admin Permissions...")
    print("=" * 50)
    
    try:
        with open('admin_credentials.json', 'r') as f:
            credentials = json.load(f)
        
        admin_email = "santhigirifmc@gmail.com"
        
        if admin_email in credentials:
            admin_data = credentials[admin_email]
            print(f"✅ Admin found: {admin_email}")
            print(f"   Role: {admin_data.get('role', 'N/A')}")
            print(f"   Status: {admin_data.get('status', 'N/A')}")
            
            permissions = admin_data.get('permissions', {})
            print("   Permissions:")
            for perm, value in permissions.items():
                status = "✅" if value else "❌"
                print(f"     {status} {perm}: {value}")
            
            # Check if has all required permissions
            required_perms = ['manage_users', 'manage_emails', 'view_analytics', 'manage_system']
            has_all = all(permissions.get(perm, False) for perm in required_perms)
            
            if has_all:
                print("\n🎉 Admin has ALL required permissions!")
                return True
            else:
                print("\n❌ Admin is missing some required permissions")
                return False
        else:
            print(f"❌ Admin {admin_email} not found in credentials")
            return False
            
    except Exception as e:
        print(f"❌ Error checking admin permissions: {e}")
        return False

def check_email_configuration():
    """Check email configuration and test connection"""
    print("\n🔍 Checking Email Configuration...")
    print("=" * 50)
    
    try:
        with open('email_accounts.json', 'r') as f:
            email_accounts = json.load(f)
        
        target_email = "smsdfinance@gmail.com"
        
        if target_email in email_accounts:
            email_data = email_accounts[target_email]
            print(f"✅ Email account found: {target_email}")
            print(f"   Display Name: {email_data.get('display_name', 'N/A')}")
            print(f"   Status: {email_data.get('status', 'N/A')}")
            print(f"   Is Default: {email_data.get('is_default', False)}")
            print(f"   Total Sent: {email_data.get('total_sent', 0)}")
            
            # Decode password
            try:
                encoded_password = email_data.get('password', '')
                decoded_password = base64.b64decode(encoded_password).decode('utf-8')
                print(f"   Password: {'*' * len(decoded_password)} (decoded successfully)")
                
                # Test email connection
                print("\n🧪 Testing email connection...")
                return test_email_connection(target_email, decoded_password)
                
            except Exception as e:
                print(f"❌ Error decoding password: {e}")
                return False
        else:
            print(f"❌ Email account {target_email} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking email configuration: {e}")
        return False

def test_email_connection(email, password):
    """Test SMTP connection to Gmail"""
    try:
        print(f"   Connecting to Gmail SMTP...")
        
        # Try Gmail SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.quit()
        
        print("   ✅ SMTP connection successful!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("   ❌ Authentication failed - check app password")
        print("   💡 Make sure you're using a Gmail App Password, not regular password")
        return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🧪 VERIFYING ADMIN & EMAIL FIXES")
    print("=" * 60)
    
    # Check admin permissions
    admin_ok = check_admin_permissions()
    
    # Check email configuration
    email_ok = check_email_configuration()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"Admin Permissions: {'✅ FIXED' if admin_ok else '❌ NEEDS FIX'}")
    print(f"Email Configuration: {'✅ WORKING' if email_ok else '❌ NEEDS FIX'}")
    
    if admin_ok and email_ok:
        print("\n🎉 ALL FIXES SUCCESSFUL!")
        print("✅ santhigirifmc@gmail.com now has full admin access")
        print("✅ smsdfinance@gmail.com is configured and working")
        print("\n📝 Next steps:")
        print("1. Restart your Streamlit app")
        print("2. Login as santhigirifmc@gmail.com")
        print("3. Access Admin Management → Email Management")
        print("4. Test sending emails")
    else:
        print("\n❌ Some issues need to be resolved:")
        if not admin_ok:
            print("- Fix admin permissions")
        if not email_ok:
            print("- Fix email configuration or app password")

if __name__ == "__main__":
    main()
