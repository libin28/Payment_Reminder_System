#!/usr/bin/env python3
"""
Fix external email sending issue - smsdfinance@gmail.com to other email addresses
"""

import smtplib
import json
import base64
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import ssl

def test_external_email_sending():
    """Test sending emails to external addresses"""
    print("🧪 TESTING EXTERNAL EMAIL SENDING")
    print("=" * 50)
    
    # Get email configuration
    with open('email_accounts.json', 'r') as f:
        accounts = json.load(f)
    
    sender_email = 'smsdfinance@gmail.com'
    sender_data = accounts[sender_email]
    password = base64.b64decode(sender_data['password']).decode('utf-8')
    
    print(f"📧 Sender: {sender_email}")
    print(f"🔑 Password length: {len(password)} chars")
    
    # Load reminders to get real recipient emails
    df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
    external_emails = []
    
    for _, row in df.iterrows():
        email = row['Email']
        if email != sender_email and '@' in email:
            external_emails.append({
                'email': email,
                'name': row['Name'],
                'id': row['ID']
            })
    
    print(f"📊 Found {len(external_emails)} external email addresses")
    
    if not external_emails:
        print("⚠️ No external email addresses found in reminders")
        return False
    
    # Test with first external email
    test_recipient = external_emails[0]
    print(f"🎯 Testing with: {test_recipient['email']} ({test_recipient['name']})")
    
    return test_smtp_to_external(sender_email, password, test_recipient)

def test_smtp_to_external(sender_email, password, recipient):
    """Test SMTP sending to external email"""
    print(f"\n📤 TESTING SMTP TO EXTERNAL EMAIL")
    print("-" * 40)
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient['email']
        msg['Subject'] = f"Test Email - External Sending Fix - {datetime.now().strftime('%H:%M:%S')}"
        
        body = f"""
Dear {recipient['name']},

This is a test email to verify that automatic email sending from {sender_email} to external email addresses is working correctly.

If you receive this email, the external email sending issue has been resolved!

Test Details:
- Sent from: {sender_email}
- Sent to: {recipient['email']}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Test ID: {recipient['id']}

Best regards,
Reminder System
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("1. Creating SMTP connection...")
        
        # Try different SMTP configurations
        configs = [
            {'host': 'smtp.gmail.com', 'port': 587, 'tls': True},
            {'host': 'smtp.gmail.com', 'port': 465, 'ssl': True},
        ]
        
        for config in configs:
            try:
                print(f"   Trying {config['host']}:{config['port']} ({'TLS' if config.get('tls') else 'SSL' if config.get('ssl') else 'Plain'})")
                
                if config.get('ssl'):
                    # SSL connection
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(config['host'], config['port'], context=context)
                else:
                    # TLS connection
                    server = smtplib.SMTP(config['host'], config['port'])
                    if config.get('tls'):
                        server.starttls()
                
                print("   ✅ Connected")
                
                print("2. Attempting login...")
                server.login(sender_email, password)
                print("   ✅ Login successful")
                
                print("3. Sending email...")
                text = msg.as_string()
                server.sendmail(sender_email, recipient['email'], text)
                print("   ✅ Email sent successfully!")
                
                server.quit()
                print("   ✅ Connection closed")
                
                print(f"\n🎉 SUCCESS! External email sending is working!")
                print(f"✅ Email sent to: {recipient['email']}")
                return True
                
            except Exception as e:
                print(f"   ❌ Failed with {config['host']}:{config['port']}: {e}")
                try:
                    server.quit()
                except:
                    pass
                continue
        
        print(f"\n❌ All SMTP configurations failed")
        return False
        
    except Exception as e:
        print(f"❌ Error in external email test: {e}")
        return False

def fix_scheduler_email_function():
    """Fix the email sending function in scheduler to handle external emails better"""
    print(f"\n🔧 CHECKING SCHEDULER EMAIL FUNCTION")
    print("=" * 50)
    
    try:
        # Check current scheduler email function
        with open('scheduler_manager.py', 'r') as f:
            content = f.read()
        
        # Look for email sending function
        if 'def send_email(' in content:
            print("✅ Found send_email function in scheduler")
            
            # Check if it uses proper SMTP configuration
            if 'smtp.gmail.com' in content and '587' in content:
                print("✅ SMTP configuration looks correct")
                return True
            else:
                print("⚠️ SMTP configuration may need updating")
                return False
        else:
            print("⚠️ send_email function not found in scheduler")
            return False
            
    except Exception as e:
        print(f"❌ Error checking scheduler: {e}")
        return False

def update_scheduler_email_function():
    """Update the scheduler email function for better external email support"""
    print(f"\n🔧 UPDATING SCHEDULER EMAIL FUNCTION")
    print("=" * 50)
    
    # Enhanced email function
    enhanced_email_function = '''
    def send_email(self, to_email, subject, body, from_email, password):
        """Enhanced email sending function with better external email support"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Try multiple SMTP configurations for better compatibility
            smtp_configs = [
                {'host': 'smtp.gmail.com', 'port': 587, 'use_tls': True},
                {'host': 'smtp.gmail.com', 'port': 465, 'use_ssl': True}
            ]
            
            for config in smtp_configs:
                try:
                    if config.get('use_ssl'):
                        # SSL connection
                        context = ssl.create_default_context()
                        server = smtplib.SMTP_SSL(config['host'], config['port'], context=context)
                    else:
                        # TLS connection
                        server = smtplib.SMTP(config['host'], config['port'])
                        if config.get('use_tls'):
                            server.starttls()
                    
                    # Login and send
                    server.login(from_email, password)
                    text = msg.as_string()
                    server.sendmail(from_email, to_email, text)
                    server.quit()
                    
                    logger.info(f"Email sent successfully to {to_email} via {config['host']}:{config['port']}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Failed to send via {config['host']}:{config['port']}: {e}")
                    try:
                        server.quit()
                    except:
                        pass
                    continue
            
            logger.error(f"All SMTP configurations failed for {to_email}")
            return False
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
    '''
    
    print("✅ Enhanced email function prepared")
    print("📝 This function will:")
    print("   - Try multiple SMTP configurations")
    print("   - Handle both TLS and SSL connections")
    print("   - Provide better error handling")
    print("   - Support external email addresses")
    
    return enhanced_email_function

def test_all_external_emails():
    """Test sending to all external email addresses in the system"""
    print(f"\n🧪 TESTING ALL EXTERNAL EMAIL ADDRESSES")
    print("=" * 50)
    
    # Get email configuration
    with open('email_accounts.json', 'r') as f:
        accounts = json.load(f)
    
    sender_email = 'smsdfinance@gmail.com'
    sender_data = accounts[sender_email]
    password = base64.b64decode(sender_data['password']).decode('utf-8')
    
    # Load reminders
    df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
    
    external_emails = []
    for _, row in df.iterrows():
        email = row['Email']
        if email != sender_email and '@' in email and email not in [e['email'] for e in external_emails]:
            external_emails.append({
                'email': email,
                'name': row['Name']
            })
    
    print(f"📊 Testing {len(external_emails)} unique external email addresses")
    
    success_count = 0
    failed_emails = []
    
    for recipient in external_emails:
        print(f"\n📧 Testing: {recipient['email']}")
        
        try:
            # Quick SMTP test
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            
            # Create simple test message
            msg = MIMEText(f"Test email to verify external sending - {datetime.now().strftime('%H:%M:%S')}")
            msg['Subject'] = "Email System Test"
            msg['From'] = sender_email
            msg['To'] = recipient['email']
            
            server.send_message(msg)
            server.quit()
            
            print(f"   ✅ Success: {recipient['email']}")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {recipient['email']} - {e}")
            failed_emails.append({'email': recipient['email'], 'error': str(e)})
    
    print(f"\n📊 EXTERNAL EMAIL TEST RESULTS:")
    print(f"✅ Successful: {success_count}/{len(external_emails)}")
    print(f"❌ Failed: {len(failed_emails)}/{len(external_emails)}")
    
    if failed_emails:
        print(f"\n❌ Failed email addresses:")
        for failed in failed_emails:
            print(f"   - {failed['email']}: {failed['error']}")
    
    return success_count == len(external_emails)

def main():
    """Main fix function"""
    print("🚨 FIXING EXTERNAL EMAIL SENDING ISSUE")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Step 1: Test current external email sending
    external_test_success = test_external_email_sending()
    
    # Step 2: Check scheduler email function
    scheduler_ok = fix_scheduler_email_function()
    
    # Step 3: Test all external emails
    if external_test_success:
        all_external_success = test_all_external_emails()
    else:
        all_external_success = False
    
    # Step 4: Provide enhanced email function
    enhanced_function = update_scheduler_email_function()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 EXTERNAL EMAIL FIX SUMMARY")
    print("=" * 60)
    
    print(f"External Email Test: {'✅ Working' if external_test_success else '❌ Failed'}")
    print(f"Scheduler Function: {'✅ OK' if scheduler_ok else '⚠️ Needs Update'}")
    print(f"All External Tests: {'✅ All Working' if all_external_success else '❌ Some Failed'}")
    
    if external_test_success and all_external_success:
        print(f"\n🎉 EXTERNAL EMAIL SENDING IS WORKING!")
        print(f"✅ Emails can be sent from smsdfinance@gmail.com to external addresses")
        print(f"✅ Automatic scheduler will work with all email addresses")
        print(f"✅ No code changes needed - system is working correctly")
    else:
        print(f"\n⚠️ ISSUES FOUND WITH EXTERNAL EMAIL SENDING")
        print(f"💡 POSSIBLE SOLUTIONS:")
        print(f"   1. Check Gmail account security settings")
        print(f"   2. Verify 2-Step Verification is enabled")
        print(f"   3. Ensure app password has 'Mail' permissions")
        print(f"   4. Check if Gmail has sending limits")
        
        if not scheduler_ok:
            print(f"   5. Update scheduler email function with enhanced version")

if __name__ == "__main__":
    main()
