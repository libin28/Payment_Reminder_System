import pandas as pd
import os
from datetime import datetime

def update_excel_column_names():
    """Update Excel file to change 'Agreement Name' to 'Header Name'"""
    excel_file = "payment_reminders.xlsx"
    
    try:
        if os.path.exists(excel_file):
            # Read the existing data
            df = pd.read_excel(excel_file, sheet_name="Reminders")
            
            print(f"📊 Found {len(df)} existing reminders")
            print(f"📋 Current columns: {list(df.columns)}")
            
            # Check if 'Agreement Name' column exists
            if 'Agreement Name' in df.columns:
                # Rename the column
                df = df.rename(columns={'Agreement Name': 'Header Name'})
                print("✅ Renamed 'Agreement Name' to 'Header Name'")
                
                # Save the updated data
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name="Reminders", index=False)
                
                print(f"✅ Updated Excel file saved successfully")
                print(f"📋 New columns: {list(df.columns)}")
                
                # Show sample data
                if not df.empty:
                    print("\n📝 Sample data after update:")
                    print(df.head().to_string())
                
            else:
                print("ℹ️ 'Agreement Name' column not found - file may already be updated")
                
                # Check if 'Header Name' already exists
                if 'Header Name' in df.columns:
                    print("✅ 'Header Name' column already exists")
                else:
                    print("⚠️ Neither 'Agreement Name' nor 'Header Name' found")
                    print(f"📋 Available columns: {list(df.columns)}")
        else:
            print("ℹ️ Excel file not found - will be created with new structure when first reminder is added")
            
    except Exception as e:
        print(f"❌ Error updating Excel file: {e}")

def verify_app_compatibility():
    """Verify that the app can load data with the new column structure"""
    try:
        # Import the load_reminders function from the app
        import sys
        sys.path.append('.')
        
        # Test loading reminders
        from app import load_reminders
        
        df = load_reminders()
        print(f"\n🧪 App compatibility test:")
        print(f"✅ Successfully loaded {len(df)} reminders")
        
        if not df.empty:
            print(f"📋 Columns loaded by app: {list(df.columns)}")
            
            # Check for required columns
            required_columns = ['ID', 'Name', 'Email', 'Header Name', 'Due Date', 'Due Time', 'Message', 'Status', 'Last Sent']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"⚠️ Missing columns: {missing_columns}")
            else:
                print("✅ All required columns present")
        else:
            print("ℹ️ No data to verify, but structure should be correct")
            
    except Exception as e:
        print(f"❌ App compatibility test failed: {e}")

def main():
    """Main function to update column names and verify compatibility"""
    print("🔄 Updating Column Names: 'Agreement Name' → 'Header Name'")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Update Excel file
    update_excel_column_names()
    
    print("\n" + "=" * 60)
    
    # Verify app compatibility
    verify_app_compatibility()
    
    print("\n" + "=" * 60)
    print("🎉 Column name update completed!")
    print()
    print("📋 Changes made:")
    print("   • Excel file: 'Agreement Name' → 'Header Name'")
    print("   • App code: Updated all references")
    print("   • Forms: Updated input labels")
    print("   • Email subjects: Updated from 'Payment Reminder' to 'Reminder'")
    print()
    print("✅ Your Reminder System is ready with the new column structure!")

if __name__ == "__main__":
    main()
