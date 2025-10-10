#!/usr/bin/env python3
"""
Direct Gmail connection test
"""

import smtplib
import base64
from email.mime.text import MIMEText

def test_gmail_connection():
    """Test Gmail connection directly"""
    
    email = "smsdfinance@gmail.com"
    # Current password from database
    encoded_password = "d2Vpbm1ocmp4cW1zcHN6cw=="
    password = base64.b64decode(encoded_password).decode('utf-8')
    
    print(f"🧪 Testing Gmail Connection")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Password length: {len(password)}")
    print("-" * 50)
    
    try:
        print("1. Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("   ✅ Connected")
        
        print("2. Starting TLS...")
        server.starttls()
        print("   ✅ TLS started")
        
        print("3. Attempting login...")
        server.login(email, password)
        print("   ✅ Login successful!")
        
        print("4. Sending test email...")
        msg = MIMEText("Test email from Reminder System")
        msg['Subject'] = "Test Email"
        msg['From'] = email
        msg['To'] = email
        
        server.send_message(msg)
        print("   ✅ Test email sent!")
        
        server.quit()
        print("   ✅ Connection closed")
        
        print("\n🎉 SUCCESS! Gmail connection is working!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        print("\n💡 This means the Gmail app password is invalid or expired.")
        print("   You need to generate a new Gmail app password.")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_gmail_connection()
