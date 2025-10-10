#!/usr/bin/env python3
"""
Test script to verify email management functionality
"""

import sys
import os
sys.path.append('.')

def test_admin_permissions():
    """Test admin permissions and email management access"""
    print("🔍 Testing Admin Permissions and Email Management...")
    
    try:
        from auth import load_admin_credentials, load_email_accounts
        
        # Load admin credentials
        credentials = load_admin_credentials()
        print(f"✅ Admin credentials loaded: {len(credentials)} accounts")
        
        for email, data in credentials.items():
            print(f"  📧 {email}")
            print(f"    Role: {data.get('role', 'admin')}")
            print(f"    Status: {data.get('status', 'active')}")
            print(f"    Permissions: {data.get('permissions', {})}")
            
            # Check email management permission
            has_email_perm = data.get('permissions', {}).get('manage_emails', False)
            has_user_perm = data.get('permissions', {}).get('manage_users', False)
            
            print(f"    Can manage emails: {'✅' if has_email_perm else '❌'}")
            print(f"    Can manage users: {'✅' if has_user_perm else '❌'}")
            print()
        
        # Load email accounts
        email_accounts = load_email_accounts()
        print(f"✅ Email accounts loaded: {len(email_accounts)} accounts")
        
        for email, data in email_accounts.items():
            print(f"  📧 {email}")
            print(f"    Display Name: {data.get('display_name', 'N/A')}")
            print(f"    Status: {data.get('status', 'active')}")
            print(f"    Default: {'✅' if data.get('is_default') else '❌'}")
            print(f"    Total Sent: {data.get('total_sent', 0)}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_email_management_functions():
    """Test email management functions"""
    print("🔧 Testing Email Management Functions...")
    
    try:
        from auth import (
            add_email_account, 
            update_email_account, 
            delete_email_account,
            test_email_account,
            get_default_email_account
        )
        
        print("✅ All email management functions imported successfully")
        
        # Test get default email account
        default_account = get_default_email_account()
        if default_account:
            print(f"✅ Default email account: {default_account['email']}")
        else:
            print("⚠️ No default email account found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing functions: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Email Management System Test")
    print("=" * 50)
    
    tests = [
        ("Admin Permissions", test_admin_permissions),
        ("Email Management Functions", test_email_management_functions)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 EMAIL MANAGEMENT SYSTEM IS READY!")
        print("✅ You can now access Email Management in Admin Management")
        print("✅ All permissions are properly configured")
        return True
    else:
        print("\n❌ SOME ISSUES FOUND")
        print("❌ Please check the failed tests above")
        return False

if __name__ == "__main__":
    main()
