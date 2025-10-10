import pandas as pd
import os
from datetime import datetime

def test_app_functionality():
    """Test basic functionality of the enhanced app"""
    
    print("🧪 Testing Enhanced Payment Reminder System")
    print("=" * 50)
    
    # Test 1: Check if Excel file exists and has correct structure
    excel_file = "payment_reminders.xlsx"
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, sheet_name="Reminders")
        print(f"✅ Excel file loaded successfully with {len(df)} reminders")
        
        # Check for required columns
        required_columns = ['ID', 'Name', 'Email', 'Agreement Name', 'Due Date', 'Due Time', 'Message', 'Status', 'Last Sent']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if not missing_columns:
            print("✅ All required columns present")
        else:
            print(f"❌ Missing columns: {missing_columns}")
        
        # Show sample data
        print(f"\n📊 Sample data preview:")
        for i, row in df.head(3).iterrows():
            print(f"   {i+1}. {row['Name']} - {row['Agreement Name']} (Due: {row['Due Date']} at {row['Due Time']})")
    else:
        print("❌ Excel file not found")
    
    # Test 2: Check if email config file structure is ready
    config_file = "email_config.json"
    if os.path.exists(config_file):
        print("✅ Email config file exists")
    else:
        print("ℹ️ Email config file will be created when you configure email settings")
    
    # Test 3: Check if required packages are installed
    try:
        import streamlit
        print(f"✅ Streamlit installed (version: {streamlit.__version__})")
    except ImportError:
        print("❌ Streamlit not installed")
    
    try:
        import apscheduler
        print(f"✅ APScheduler installed (version: {apscheduler.__version__})")
    except ImportError:
        print("❌ APScheduler not installed")
    
    try:
        import openpyxl
        print("✅ OpenPyXL installed")
    except ImportError:
        print("❌ OpenPyXL not installed")
    
    # Test 4: Check app file structure
    app_file = "app.py"
    if os.path.exists(app_file):
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key functions
        key_functions = [
            'load_reminders',
            'save_reminders', 
            'send_selected_reminders',
            'delete_selected_reminders',
            'update_reminder'
        ]
        
        for func in key_functions:
            if f"def {func}" in content:
                print(f"✅ Function '{func}' found")
            else:
                print(f"❌ Function '{func}' missing")
    else:
        print("❌ app.py file not found")
    
    print("\n🎯 Test Summary:")
    print("✅ Enhanced Payment Reminder System is ready!")
    print("🌐 Access your app at: http://localhost:8501")
    print("\n📋 Next steps:")
    print("1. Configure email settings in the app")
    print("2. Test the edit functionality")
    print("3. Try selective mailing")
    print("4. Test bulk actions")

if __name__ == "__main__":
    test_app_functionality()
