#!/usr/bin/env python3
"""
Fix the Gmail app password for smsdfinance@gmail.com
"""

import json
import base64

def fix_email_password():
    """Fix the email password by removing spaces"""
    
    # Current password with spaces
    current_password = "wein mhrj xqms pszs"
    
    # Remove spaces to get proper 16-character app password
    fixed_password = current_password.replace(" ", "")
    
    print(f"Current password: '{current_password}' ({len(current_password)} chars)")
    print(f"Fixed password:   '{fixed_password}' ({len(fixed_password)} chars)")
    
    if len(fixed_password) == 16:
        print("✅ Password length is correct for Gmail app password")
        
        # Encode the fixed password
        encoded_password = base64.b64encode(fixed_password.encode('utf-8')).decode('utf-8')
        
        # Update the email accounts file
        with open('email_accounts.json', 'r') as f:
            accounts = json.load(f)
        
        if 'smsdfinance@gmail.com' in accounts:
            accounts['smsdfinance@gmail.com']['password'] = encoded_password
            
            with open('email_accounts.json', 'w') as f:
                json.dump(accounts, f, indent=4)
            
            print("✅ Email password updated successfully!")
            return True
        else:
            print("❌ Email account not found")
            return False
    else:
        print(f"❌ Password length is {len(fixed_password)}, should be 16")
        return False

if __name__ == "__main__":
    print("🔧 FIXING EMAIL PASSWORD")
    print("=" * 40)
    
    success = fix_email_password()
    
    if success:
        print("\n🎉 Email password fixed!")
        print("📝 Next steps:")
        print("1. Test the email connection")
        print("2. Try sending a test email")
    else:
        print("\n❌ Failed to fix email password")
        print("💡 You may need to generate a new Gmail app password")
