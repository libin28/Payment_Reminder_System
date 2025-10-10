#!/usr/bin/env python3
"""
Fix the email password encoding issue
"""

import base64
import json

# The correct password from email_config.json
correct_password = "pumk wwbj pwtr jzhp"

print(f"Original password: '{correct_password}'")

# Encode it properly
encoded_password = base64.b64encode(correct_password.encode('utf-8')).decode('utf-8')
print(f"Correctly encoded password: '{encoded_password}'")

# Test decoding
try:
    decoded_test = base64.b64decode(encoded_password).decode('utf-8')
    print(f"Decoded test: '{decoded_test}'")
    if decoded_test == correct_password:
        print("✅ Encoding/decoding works correctly!")
    else:
        print("❌ Encoding/decoding failed!")
except Exception as e:
    print(f"❌ Error in test: {e}")

# Update email_accounts.json
try:
    with open('email_accounts.json', 'r') as f:
        accounts = json.load(f)
    
    # Update the password
    for email, data in accounts.items():
        if email == 'liblal2018@gmail.com':
            old_password = data['password']
            data['password'] = encoded_password
            print(f"Updated password for {email}")
            print(f"  Old: {old_password}")
            print(f"  New: {encoded_password}")
    
    # Save the updated accounts
    with open('email_accounts.json', 'w') as f:
        json.dump(accounts, f, indent=2)
    
    print("✅ Email accounts file updated successfully")
    
except Exception as e:
    print(f"❌ Error updating email accounts: {e}")

# Verify the update
try:
    with open('email_accounts.json', 'r') as f:
        accounts = json.load(f)
    
    for email, data in accounts.items():
        if email == 'liblal2018@gmail.com':
            stored_password = data['password']
            decoded_stored = base64.b64decode(stored_password).decode('utf-8')
            print(f"Verification - stored password decodes to: '{decoded_stored}'")
            if decoded_stored == correct_password:
                print("✅ Password stored and verified correctly!")
            else:
                print("❌ Password verification failed!")
                
except Exception as e:
    print(f"❌ Error verifying password: {e}")
