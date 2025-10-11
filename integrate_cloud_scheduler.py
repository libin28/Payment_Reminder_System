#!/usr/bin/env python3
"""
Integrate cloud scheduler into app.py for Streamlit Cloud deployment
"""

import re

def add_cloud_scheduler_import():
    """Add cloud scheduler import to app.py"""
    
    import_line = "from streamlit_cloud_scheduler import get_cloud_scheduler, show_cloud_scheduler_status, initialize_cloud_scheduler"
    
    print("📝 ADDING CLOUD SCHEDULER IMPORT")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if import already exists
        if 'streamlit_cloud_scheduler' in content:
            print("✅ Cloud scheduler import already exists")
            return True
        
        # Find the last import line
        import_pattern = r'^(import\s+\w+|from\s+\w+.*import.*)'
        lines = content.split('\n')
        last_import_line = -1
        
        for i, line in enumerate(lines):
            if re.match(import_pattern, line.strip()):
                last_import_line = i
        
        if last_import_line >= 0:
            # Insert after last import
            lines.insert(last_import_line + 1, import_line)
            
            # Write back to file
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Added cloud scheduler import after line {last_import_line + 1}")
            return True
        else:
            print("❌ Could not find import section")
            return False
            
    except Exception as e:
        print(f"❌ Error adding import: {e}")
        return False

def add_cloud_scheduler_setup():
    """Add cloud scheduler setup function"""
    
    setup_function = '''
def setup_cloud_scheduler():
    """Setup cloud scheduler for automatic emails"""
    if 'cloud_scheduler_setup' not in st.session_state:
        st.session_state.cloud_scheduler_setup = True
        initialize_cloud_scheduler()
'''
    
    print("\n📝 ADDING CLOUD SCHEDULER SETUP FUNCTION")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if function already exists
        if 'setup_cloud_scheduler' in content:
            print("✅ Cloud scheduler setup function already exists")
            return True
        
        # Find a good place to insert the function (after other function definitions)
        # Look for the main app logic or after load_reminders function
        insertion_point = content.find('def main():')
        if insertion_point == -1:
            insertion_point = content.find('if __name__ == "__main__":')
        if insertion_point == -1:
            insertion_point = content.find('st.title(')
        
        if insertion_point > 0:
            # Insert before the main logic
            content = content[:insertion_point] + setup_function + '\n' + content[insertion_point:]
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Added cloud scheduler setup function")
            return True
        else:
            print("❌ Could not find suitable insertion point")
            return False
            
    except Exception as e:
        print(f"❌ Error adding setup function: {e}")
        return False

def add_cloud_scheduler_call():
    """Add call to setup_cloud_scheduler in main app logic"""
    
    print("\n📝 ADDING CLOUD SCHEDULER CALL")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if call already exists
        if 'setup_cloud_scheduler()' in content:
            print("✅ Cloud scheduler call already exists")
            return True
        
        # Find where to add the call (after login logic)
        # Look for successful login or main app logic
        patterns = [
            r'if\s+st\.session_state\.get\(["\']logged_in["\'].*?\):\s*\n',
            r'if\s+logged_in:\s*\n',
            r'st\.sidebar\.title\(',
            r'page\s*=\s*st\.sidebar\.selectbox\('
        ]
        
        insertion_point = -1
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                insertion_point = match.end()
                break
        
        if insertion_point > 0:
            # Insert the call
            call_line = "    setup_cloud_scheduler()\n    \n"
            content = content[:insertion_point] + call_line + content[insertion_point:]
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Added cloud scheduler call in main app logic")
            return True
        else:
            print("❌ Could not find suitable place to add scheduler call")
            print("💡 You'll need to manually add 'setup_cloud_scheduler()' after login")
            return False
            
    except Exception as e:
        print(f"❌ Error adding scheduler call: {e}")
        return False

def update_scheduler_status_page():
    """Update the scheduler status page to use cloud scheduler"""
    
    print("\n📝 UPDATING SCHEDULER STATUS PAGE")
    print("=" * 40)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the scheduler status page
        scheduler_page_pattern = r'elif\s+page\s*==\s*["\'].*Scheduler Status.*["\']:\s*\n(.*?)(?=elif\s+page\s*==|if\s+__name__|$)'
        
        match = re.search(scheduler_page_pattern, content, re.DOTALL)
        
        if match:
            old_page_content = match.group(0)
            
            new_page_content = '''elif page == "🔧 Scheduler Status":
        st.title("🔧 Scheduler Status")
        
        # Show cloud scheduler status
        show_cloud_scheduler_status()
        
        # Show current time
        st.info(f"🕐 Current Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show reminders summary
        try:
            df = pd.read_excel('payment_reminders.xlsx', sheet_name='Reminders')
            active_reminders = df[df.get('Status', 'Active') == 'Active']
            st.metric("📋 Active Reminders", len(active_reminders))
            
            # Show next few due reminders
            now = datetime.now()
            upcoming = []
            for _, row in active_reminders.iterrows():
                try:
                    due_date = pd.to_datetime(row['Due Date']).date()
                    due_time = datetime.strptime(row.get('Due Time', '09:00'), '%H:%M').time()
                    scheduled_datetime = datetime.combine(due_date, due_time)
                    
                    if scheduled_datetime > now and (pd.isna(row.get('Last Sent', '')) or row.get('Last Sent', '') == ''):
                        upcoming.append({
                            'name': row['Name'],
                            'email': row['Email'],
                            'time': scheduled_datetime
                        })
                except:
                    continue
            
            upcoming.sort(key=lambda x: x['time'])
            
            if upcoming:
                st.subheader("📅 Upcoming Reminders")
                for reminder in upcoming[:5]:
                    st.info(f"📧 {reminder['name']} ({reminder['email']}) - {reminder['time'].strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            st.error(f"Error loading reminders: {e}")

'''
            
            # Replace the old page content with new
            content = content.replace(old_page_content, new_page_content)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Updated scheduler status page with cloud scheduler")
            return True
        else:
            print("⚠️ Could not find scheduler status page to update")
            print("💡 You may need to manually update the scheduler status page")
            return False
            
    except Exception as e:
        print(f"❌ Error updating scheduler status page: {e}")
        return False

def create_requirements_txt():
    """Create or update requirements.txt for Streamlit Cloud"""
    
    print("\n📝 CREATING/UPDATING REQUIREMENTS.TXT")
    print("=" * 40)
    
    requirements = """streamlit>=1.28.0
pandas>=1.5.0
openpyxl>=3.0.0
bcrypt>=4.0.0
APScheduler>=3.10.0
email-validator>=2.0.0
"""
    
    try:
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        
        print("✅ Created/updated requirements.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error creating requirements.txt: {e}")
        return False

def main():
    """Main integration function"""
    print("🚀 INTEGRATING CLOUD SCHEDULER INTO APP.PY")
    print("=" * 60)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Add import
    if add_cloud_scheduler_import():
        success_count += 1
    
    # Step 2: Add setup function
    if add_cloud_scheduler_setup():
        success_count += 1
    
    # Step 3: Add scheduler call
    if add_cloud_scheduler_call():
        success_count += 1
    
    # Step 4: Update scheduler status page
    if update_scheduler_status_page():
        success_count += 1
    
    # Step 5: Create requirements.txt
    if create_requirements_txt():
        success_count += 1
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 INTEGRATION SUMMARY")
    print("=" * 60)
    
    print(f"✅ Successful steps: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print(f"\n🎉 INTEGRATION COMPLETE!")
        print(f"✅ Cloud scheduler fully integrated into app.py")
        print(f"✅ Requirements.txt updated")
        print(f"✅ Ready for Streamlit Cloud deployment")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Upload streamlit_cloud_scheduler.py to your GitHub repo")
        print(f"2. Upload the modified app.py to your GitHub repo")
        print(f"3. Upload requirements.txt to your GitHub repo")
        print(f"4. Redeploy your Streamlit app")
        print(f"5. Test the 'Check Due Emails Now' button")
        print(f"6. Schedule a test reminder for a few minutes ahead")
        
    elif success_count >= 3:
        print(f"\n⚠️ PARTIAL INTEGRATION COMPLETE")
        print(f"✅ Core functionality integrated")
        print(f"💡 Some manual adjustments may be needed")
        print(f"📖 Check STREAMLIT_CLOUD_INTEGRATION_GUIDE.md for manual steps")
        
    else:
        print(f"\n❌ INTEGRATION INCOMPLETE")
        print(f"💡 Manual integration required")
        print(f"📖 Follow STREAMLIT_CLOUD_INTEGRATION_GUIDE.md for manual steps")

if __name__ == "__main__":
    main()
