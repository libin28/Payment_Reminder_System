#!/usr/bin/env python3
"""
Quick test to verify Streamlit app starts without errors
"""

import streamlit as st
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_import():
    """Test if the app can be imported without errors"""
    try:
        # Try to import the main modules
        from auth import load_admin_credentials, is_admin_logged_in
        from scheduler_manager import EmailScheduler
        
        print("✅ Core modules imported successfully")
        
        # Test basic functions
        credentials = load_admin_credentials()
        print(f"✅ Admin credentials loaded: {len(credentials)} accounts")
        
        # Test email scheduler
        scheduler = EmailScheduler()
        print("✅ Email scheduler initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing modules: {e}")
        return False

def test_streamlit_syntax():
    """Test if app.py has valid Python syntax"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile the code
        compile(content, 'app.py', 'exec')
        print("✅ app.py has valid Python syntax")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Streamlit App...")
    print("=" * 50)
    
    # Test syntax first
    syntax_ok = test_streamlit_syntax()
    
    if syntax_ok:
        # Test imports
        import_ok = test_app_import()
        
        if import_ok:
            print("\n🎉 All tests passed! App should start successfully.")
            print("\n📝 To start the app, run:")
            print("   streamlit run app.py")
        else:
            print("\n❌ Import tests failed. Check the error messages above.")
    else:
        print("\n❌ Syntax tests failed. Fix syntax errors first.")
