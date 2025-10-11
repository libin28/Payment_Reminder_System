#!/usr/bin/env python3
"""
Simple scheduler test and fix
"""

from scheduler_manager import get_scheduler
import pandas as pd
from datetime import datetime, timedelta
import uuid

def main():
    print("🧪 SIMPLE SCHEDULER TEST")
    print("=" * 40)
    
    # Get scheduler
    scheduler = get_scheduler()
    print(f"Scheduler running: {scheduler.scheduler.running}")
    
    # Check current jobs
    jobs = scheduler.get_scheduled_jobs()
    print(f"Current jobs: {len(jobs)}")
    
    # Create test reminder for 3 minutes from now
    test_time = datetime.now() + timedelta(minutes=3)
    test_date = test_time.date()
    test_time_str = test_time.strftime('%H:%M')
    
    print(f"Scheduling test for: {test_date} {test_time_str}")
    
    # Schedule test
    test_id = str(uuid.uuid4())
    success = scheduler.schedule_reminder(test_id, test_date, test_time_str)
    print(f"Schedule success: {success}")
    
    # Check jobs after
    jobs = scheduler.get_scheduled_jobs()
    print(f"Jobs after test: {len(jobs)}")
    
    if jobs:
        for job in jobs:
            print(f"  Job: {job['id']} at {job['next_run']}")
    
    # Test manual email send
    print("\nTesting manual email send...")
    try:
        result = scheduler.send_reminder_email(test_id)
        print(f"Manual send result: {result}")
    except Exception as e:
        print(f"Manual send error: {e}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
