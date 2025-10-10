#!/usr/bin/env python3
"""
Create the correct base64 encoded password and update email_accounts.json
"""

import base64
import json

# The correct password
password = "pumk wwbj pwtr jzhp"

# Encode it
encoded = base64.b64encode(password.encode('utf-8')).decode('utf-8')

print(f"Password: '{password}'")
print(f"Encoded: '{encoded}'")

# Test decoding
decoded = base64.b64decode(encoded).decode('utf-8')
print(f"Decoded: '{decoded}'")

if decoded == password:
    print("✅ Encoding/decoding works!")
else:
    print("❌ Encoding/decoding failed!")

print(f"\nCorrect base64 value to use: {encoded}")

# Update email_accounts.json
try:
    with open('email_accounts.json', 'r') as f:
        accounts = json.load(f)

    # Update the password
    for email, data in accounts.items():
        if email == 'liblal2018@gmail.com':
            old_password = data['password']
            data['password'] = encoded
            print(f"\nUpdated password for {email}")
            print(f"  Old: {old_password}")
            print(f"  New: {encoded}")

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
            print(f"\nVerification - stored password decodes to: '{decoded_stored}'")
            if decoded_stored == password:
                print("✅ Password stored and verified correctly!")
            else:
                print("❌ Password verification failed!")

except Exception as e:
    print(f"❌ Error verifying password: {e}")
