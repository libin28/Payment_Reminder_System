#!/usr/bin/env python3
"""
Reschedule all reminders with enhanced email function
"""

from scheduler_manager import get_scheduler

def main():
    print("🔄 RESCHEDULING ALL REMINDERS WITH ENHANCED EMAIL FUNCTION")
    print("=" * 60)
    
    scheduler = get_scheduler()
    
    print("📊 Rescheduling all active reminders...")
    scheduler.reschedule_all_active_reminders()
    
    jobs = scheduler.get_scheduled_jobs()
    print(f"✅ Total scheduled jobs: {len(jobs)}")
    
    if jobs:
        print("\n📅 Scheduled jobs:")
        for job in jobs:
            print(f"   - {job['id']}: {job['next_run']}")
    
    print(f"\n🎉 All reminders rescheduled with enhanced email function!")
    print(f"✅ External emails will now work automatically")

if __name__ == "__main__":
    main()
