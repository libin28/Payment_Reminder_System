import pandas as pd
from datetime import datetime, timedelta

# Create sample data for payment reminders
sample_data = [
    {
        'Name': 'John Smith',
        'Email': 'john.smith@example.com',
        'Agreement Name': 'Monthly Rent Payment',
        'Due Date': datetime.today().date(),  # Due today for testing
        'Message': 'This is a friendly reminder that your monthly rent payment of $1,200 is due today. Please ensure payment is made by end of business day to avoid any late fees.',
        'Status': 'Active',
        'Last Sent': ''
    },
    {
        'Name': 'Sarah Johnson',
        'Email': 'sarah.j@example.com',
        'Agreement Name': 'Office Lease Payment',
        'Due Date': datetime.today().date() + timedelta(days=3),  # Due in 3 days
        'Message': 'Dear Sarah, this is a reminder that your office lease payment of $2,500 is due in 3 days. Thank you for your prompt attention to this matter.',
        'Status': 'Active',
        'Last Sent': ''
    },
    {
        'Name': 'Mike Wilson',
        'Email': 'mike.wilson@example.com',
        'Agreement Name': 'Equipment Rental Fee',
        'Due Date': datetime.today().date() + timedelta(days=7),  # Due in a week
        'Message': 'Hi Mike, this is a reminder that your monthly equipment rental fee of $800 is due next week. Please arrange for payment at your earliest convenience.',
        'Status': 'Active',
        'Last Sent': ''
    },
    {
        'Name': 'Lisa Brown',
        'Email': 'lisa.brown@example.com',
        'Agreement Name': 'Service Contract Payment',
        'Due Date': datetime.today().date() + timedelta(days=15),  # Due in 15 days
        'Message': 'Dear Lisa, this is a reminder that your service contract payment of $1,500 is due in two weeks. We appreciate your continued business.',
        'Status': 'Active',
        'Last Sent': ''
    },
    {
        'Name': 'David Lee',
        'Email': 'david.lee@example.com',
        'Agreement Name': 'Consulting Fee',
        'Due Date': datetime.today().date() - timedelta(days=2),  # Overdue by 2 days
        'Message': 'Dear David, this is a reminder that your consulting fee payment of $3,000 was due 2 days ago. Please arrange for immediate payment.',
        'Status': 'Active',
        'Last Sent': ''
    }
]

# Create DataFrame
df = pd.DataFrame(sample_data)

# Save to Excel file
with pd.ExcelWriter('payment_reminders.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Reminders', index=False)

print("✅ Sample payment reminders Excel file created successfully!")
print(f"📊 Created {len(sample_data)} sample reminders")
print("\nSample data includes:")
for i, reminder in enumerate(sample_data, 1):
    print(f"{i}. {reminder['Name']} - {reminder['Agreement Name']} (Due: {reminder['Due Date']})")
