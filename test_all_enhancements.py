import pandas as pd
import os
import json
from datetime import datetime
import requests
import time

def test_app_name_changes():
    """Test that app name has been changed from 'Payment Reminder System' to 'Reminder System'"""
    print("🔍 Testing App Name Changes...")
    
    # Check app.py for title changes
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Check for old references
    old_references = app_content.count('Payment Reminder System')
    payment_references = app_content.count('Payment Reminder')
    
    print(f"   📊 'Payment Reminder System' references found: {old_references}")
    print(f"   📊 'Payment Reminder' references found: {payment_references}")
    
    # Check for new references
    new_references = app_content.count('Reminder System')
    
    print(f"   ✅ 'Reminder System' references found: {new_references}")
    
    # Check auth.py
    with open('auth.py', 'r', encoding='utf-8') as f:
        auth_content = f.read()
    
    auth_old_refs = auth_content.count('Payment Reminder System')
    auth_new_refs = auth_content.count('Reminder System')
    
    print(f"   📊 Auth.py - Old references: {auth_old_refs}, New references: {auth_new_refs}")
    
    if old_references == 0 and new_references > 0:
        print("   ✅ App name successfully updated!")
    else:
        print("   ⚠️ Some old references may still exist")
    
    return old_references == 0

def test_header_name_changes():
    """Test that 'Agreement Name' has been changed to 'Header Name'"""
    print("\n🔍 Testing Header Name Changes...")
    
    # Check app.py for field changes
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Check for old references
    old_field_refs = app_content.count('Agreement Name')
    header_field_refs = app_content.count('Header Name')
    
    print(f"   📊 'Agreement Name' references found: {old_field_refs}")
    print(f"   ✅ 'Header Name' references found: {header_field_refs}")
    
    # Check Excel file structure
    if os.path.exists('payment_reminders.xlsx'):
        try:
            df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
            columns = list(df.columns)
            print(f"   📋 Excel columns: {columns}")
            
            has_header_name = 'Header Name' in columns
            has_agreement_name = 'Agreement Name' in columns
            
            print(f"   ✅ Has 'Header Name' column: {has_header_name}")
            print(f"   📊 Has 'Agreement Name' column: {has_agreement_name}")
            
            if has_header_name and not has_agreement_name:
                print("   ✅ Excel file structure updated successfully!")
                return True
            else:
                print("   ⚠️ Excel file may need updating")
                return False
        except Exception as e:
            print(f"   ❌ Error reading Excel file: {e}")
            return False
    else:
        print("   ℹ️ Excel file not found - will be created with correct structure")
        return True

def test_admin_management_enhancements():
    """Test that admin management enhancements are in place"""
    print("\n🔍 Testing Admin Management Enhancements...")
    
    # Check auth.py for new functions
    with open('auth.py', 'r', encoding='utf-8') as f:
        auth_content = f.read()
    
    # Check for new functions
    functions_to_check = [
        'change_admin_email',
        'change_admin_password',
        'Edit Admin Details'
    ]
    
    found_functions = []
    for func in functions_to_check:
        if func in auth_content:
            found_functions.append(func)
            print(f"   ✅ Found: {func}")
        else:
            print(f"   ❌ Missing: {func}")
    
    # Check for tab structure
    tab_count = auth_content.count('with tab')
    print(f"   📊 Admin management tabs found: {tab_count}")
    
    if len(found_functions) >= 2:
        print("   ✅ Admin management enhancements implemented!")
        return True
    else:
        print("   ⚠️ Some admin management features may be missing")
        return False

def test_app_functionality():
    """Test basic app functionality"""
    print("\n🔍 Testing App Functionality...")
    
    try:
        # Test app loading
        response = requests.get('http://localhost:8501', timeout=5)
        if response.status_code == 200:
            print("   ✅ App is running and accessible")
            
            # Check if login page is displayed
            if 'Admin Login' in response.text or 'login' in response.text.lower():
                print("   ✅ Login page is displayed")
            else:
                print("   ⚠️ Login page may not be displayed correctly")
            
            return True
        else:
            print(f"   ❌ App returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error accessing app: {e}")
        return False

def test_data_integrity():
    """Test that existing data is preserved"""
    print("\n🔍 Testing Data Integrity...")
    
    try:
        # Load reminders using app function
        import sys
        sys.path.append('.')
        from app import load_reminders
        
        df = load_reminders()
        print(f"   📊 Loaded {len(df)} reminders")
        
        if not df.empty:
            # Check required columns
            required_columns = ['ID', 'Name', 'Email', 'Header Name', 'Due Date', 'Due Time', 'Message', 'Status']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"   ❌ Missing columns: {missing_columns}")
                return False
            else:
                print("   ✅ All required columns present")
                
                # Check data types and content
                print(f"   📋 Sample data preview:")
                for idx, row in df.head(2).iterrows():
                    print(f"      • {row['Name']} - {row['Header Name']}")
                
                return True
        else:
            print("   ℹ️ No existing data to verify")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing data integrity: {e}")
        return False

def test_email_subject_updates():
    """Test that email subjects have been updated"""
    print("\n🔍 Testing Email Subject Updates...")
    
    # Check app.py for email subject changes
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Count old vs new email subjects
    old_subjects = app_content.count('Payment Reminder -')
    new_subjects = app_content.count('Reminder -')
    
    print(f"   📊 'Payment Reminder -' subjects found: {old_subjects}")
    print(f"   ✅ 'Reminder -' subjects found: {new_subjects}")
    
    if old_subjects == 0 and new_subjects > 0:
        print("   ✅ Email subjects successfully updated!")
        return True
    else:
        print("   ⚠️ Some email subjects may need updating")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE ENHANCEMENT TEST REPORT")
    print("="*80)
    print(f"🕐 Test executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    tests = [
        ("App Name Changes", test_app_name_changes),
        ("Header Name Changes", test_header_name_changes),
        ("Admin Management Enhancements", test_admin_management_enhancements),
        ("App Functionality", test_app_functionality),
        ("Data Integrity", test_data_integrity),
        ("Email Subject Updates", test_email_subject_updates)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ Test '{test_name}' failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL ENHANCEMENTS SUCCESSFULLY IMPLEMENTED!")
        print("✅ Your Reminder System is ready for production use!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed - please review the issues above")
    
    print("\n" + "="*80)
    
    return passed == total

if __name__ == "__main__":
    success = generate_test_report()
    
    if success:
        print("\n🚀 READY TO USE YOUR ENHANCED REMINDER SYSTEM!")
        print("📧 Access your app at: http://localhost:8501")
        print("🔐 Default login: admin@reminder.com / Admin@123")
    else:
        print("\n🔧 Please address the failed tests before using the system")
