import subprocess
import sys
import os
import threading
import time

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_sample_data():
    """Create sample data if Excel file doesn't exist"""
    if not os.path.exists("payment_reminders.xlsx"):
        print("Creating sample data...")
        try:
            subprocess.check_call([sys.executable, "create_sample_data.py"])
            print("✅ Sample data created!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating sample data: {e}")

def start_scheduler():
    """Start the background scheduler"""
    print("⏰ Starting background scheduler...")
    try:
        # Run scheduler in background
        subprocess.Popen([sys.executable, "scheduler.py"])
        print("✅ Scheduler started in background!")
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")

def start_streamlit():
    """Start the Streamlit app"""
    print("🚀 Starting Streamlit app...")
    try:
        subprocess.check_call([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"])
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

def main():
    print("💰 Payment Reminder System")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Exiting.")
        return
    
    # Create sample data
    create_sample_data()
    
    # Start scheduler in background
    start_scheduler()
    
    # Give scheduler time to start
    time.sleep(2)
    
    print("\n🌐 Starting web application...")
    print("📱 The app will open in your browser at: http://localhost:8501")
    print("⏰ Background scheduler is running to send automatic reminders")
    print("\n💡 Tips:")
    print("   - Configure your email settings first")
    print("   - Add your payment reminders")
    print("   - The system will automatically send reminders on due dates")
    print("\n🛑 Press Ctrl+C to stop the application")
    print("=" * 40)
    
    # Start Streamlit app
    start_streamlit()

if __name__ == "__main__":
    main()
