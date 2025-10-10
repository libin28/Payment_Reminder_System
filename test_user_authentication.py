#!/usr/bin/env python3
"""
Test User Authentication Enhancement
Tests the new user registration and authentication functionality
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path to import auth module
sys.path.append('.')

def test_user_registration():
    """Test user account creation functionality"""
    print("🧪 Testing User Registration Features")
    print("=" * 50)
    
    try:
        from auth import (
            create_user_account,
            authenticate_user,
            load_user_accounts,
            validate_password_strength,
            validate_email_format,
            update_user_status,
            delete_user_account
        )
        
        print("✅ Successfully imported user authentication functions")
        
        # Test 1: Email validation
        print("\n📝 Test 1: Email Format Validation")
        valid_emails = ["test@example.com", "user.name@domain.co.uk", "admin@reminder.com"]
        invalid_emails = ["invalid-email", "@domain.com", "user@", "user.domain.com"]
        
        for email in valid_emails:
            result = validate_email_format(email)
            print(f"  ✅ {email}: {result['valid']} - {result['message']}")
        
        for email in invalid_emails:
            result = validate_email_format(email)
            print(f"  ❌ {email}: {result['valid']} - {result['message']}")
        
        # Test 2: Password strength validation
        print("\n📝 Test 2: Password Strength Validation")
        passwords = [
            ("Password123", True),
            ("password123", False),  # No uppercase
            ("PASSWORD123", False),  # No lowercase
            ("Password", False),     # No number
            ("Pass1", False),        # Too short
            ("MySecurePass123", True)
        ]
        
        for password, should_be_valid in passwords:
            result = validate_password_strength(password)
            status = "✅" if result['valid'] == should_be_valid else "❌"
            print(f"  {status} '{password}': {result['valid']} - {result['message']}")
        
        # Test 3: User account creation
        print("\n📝 Test 3: User Account Creation")
        test_users = [
            ("testuser1@example.com", "TestPass123", "TestPass123", True),
            ("testuser2@example.com", "TestPass456", "TestPass456", True),
            ("invalid@email", "TestPass123", "TestPass123", False),  # Invalid email
            ("testuser1@example.com", "TestPass123", "TestPass123", False),  # Duplicate
            ("testuser3@example.com", "TestPass123", "DifferentPass", False),  # Password mismatch
            ("testuser4@example.com", "weak", "weak", False),  # Weak password
        ]
        
        for email, password, confirm_password, should_succeed in test_users:
            result = create_user_account(email, password, confirm_password)
            status = "✅" if result['success'] == should_succeed else "❌"
            print(f"  {status} {email}: {result['success']} - {result['message']}")
        
        # Test 4: User authentication
        print("\n📝 Test 4: User Authentication")
        auth_tests = [
            ("testuser1@example.com", "TestPass123", True),   # Valid login
            ("testuser1@example.com", "WrongPass", False),    # Wrong password
            ("nonexistent@example.com", "TestPass123", False), # Non-existent user
            ("testuser2@example.com", "TestPass456", True),   # Another valid login
        ]
        
        for email, password, should_succeed in auth_tests:
            result = authenticate_user(email, password)
            status = "✅" if result['success'] == should_succeed else "❌"
            print(f"  {status} {email}: {result['success']} - {result['message']}")
        
        # Test 5: Load user accounts
        print("\n📝 Test 5: Load User Accounts")
        user_accounts = load_user_accounts()
        print(f"Loaded {len(user_accounts)} user accounts:")
        
        for email, data in user_accounts.items():
            print(f"  👤 {email}")
            print(f"     Status: {data.get('status', 'N/A')}")
            print(f"     Created: {data.get('created_at', 'N/A')}")
            print(f"     Last Login: {data.get('last_login', 'Never')}")
        
        # Test 6: User status management
        print("\n📝 Test 6: User Status Management")
        if "testuser1@example.com" in user_accounts:
            # Test deactivation
            result = update_user_status("testuser1@example.com", "inactive", "admin@test.com")
            print(f"  Deactivate user: {result['success']} - {result['message']}")
            
            # Test authentication with inactive account
            result = authenticate_user("testuser1@example.com", "TestPass123")
            print(f"  Login with inactive account: {result['success']} - {result['message']}")
            
            # Test reactivation
            result = update_user_status("testuser1@example.com", "active", "admin@test.com")
            print(f"  Reactivate user: {result['success']} - {result['message']}")
        
        # Test 7: Account lockout simulation
        print("\n📝 Test 7: Account Lockout Simulation")
        if "testuser2@example.com" in user_accounts:
            print("  Simulating 5 failed login attempts...")
            for i in range(5):
                result = authenticate_user("testuser2@example.com", "WrongPassword")
                print(f"    Attempt {i+1}: {result['message']}")
            
            # Try one more time to trigger lockout
            result = authenticate_user("testuser2@example.com", "WrongPassword")
            print(f"  Final attempt: {result['success']} - {result['message']}")
        
        print("\n🎉 User Registration Tests Completed!")
        
        # Show final state
        print("\n📊 Final User Accounts State:")
        final_accounts = load_user_accounts()
        if final_accounts:
            for email, data in final_accounts.items():
                status_icon = "✅" if data.get('status') == 'active' else "❌"
                locked_icon = "🔒" if data.get('locked_until') else ""
                attempts = data.get('login_attempts', 0)
                print(f"  {status_icon} {email} {locked_icon}")
                print(f"     Status: {data.get('status', 'unknown')}")
                print(f"     Failed attempts: {attempts}/5")
        else:
            print("  No user accounts found")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure auth.py is in the current directory")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

def test_login_page_integration():
    """Test login page integration"""
    print("\n🔗 Testing Login Page Integration")
    print("=" * 40)
    
    try:
        from auth import show_login_page, is_admin_logged_in, is_user_logged_in
        
        print("✅ Login page functions imported successfully")
        print("📝 Login page integration requires manual testing through web interface")
        print("   - Test admin login with existing credentials")
        print("   - Test user registration through Create Account tab")
        print("   - Test user login with newly created account")
        print("   - Test error handling for invalid inputs")
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")

def cleanup_test_accounts():
    """Clean up test accounts created during testing"""
    print("\n🧹 Cleaning Up Test Accounts")
    print("=" * 35)
    
    try:
        from auth import delete_user_account, load_user_accounts
        
        user_accounts = load_user_accounts()
        test_emails = [email for email in user_accounts.keys() if "test" in email.lower()]
        
        if test_emails:
            print(f"Found {len(test_emails)} test accounts to clean up:")
            for email in test_emails:
                result = delete_user_account(email, "test_cleanup")
                status = "✅" if result['success'] else "❌"
                print(f"  {status} Deleted {email}: {result['message']}")
        else:
            print("No test accounts found to clean up")
            
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

if __name__ == "__main__":
    print("🚀 Starting User Authentication Enhancement Tests")
    print("=" * 70)
    
    test_user_registration()
    test_login_page_integration()
    
    # Ask user if they want to clean up test accounts
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    
    print("\n📋 Next Steps for Manual Testing:")
    print("1. Start your Reminder System: python -m streamlit run app.py")
    print("2. Test the new Create Account tab on login page")
    print("3. Register a new user account")
    print("4. Login with the new user account")
    print("5. Verify user has limited navigation options")
    print("6. Login as admin and check User Accounts tab in Admin Management")
    print("7. Test admin controls: activate/deactivate/delete user accounts")
    
    # Optionally clean up test accounts
    cleanup_choice = input("\n🧹 Clean up test accounts? (y/n): ").lower().strip()
    if cleanup_choice in ['y', 'yes']:
        cleanup_test_accounts()
    else:
        print("Test accounts preserved for manual inspection")
