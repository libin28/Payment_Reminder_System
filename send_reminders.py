import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime

# 1️⃣ Your email credentials
SENDER_EMAIL = "yourmail@gmail.com"
APP_PASSWORD = "your_app_password"  # Generated from Google account

# 2️⃣ Load Excel file
df = pd.read_excel("payment_reminders.xlsx", sheet_name="Reminders")

# 3️⃣ Today's date
today_str = datetime.today().strftime('%d-%m-%Y')

# 4️⃣ Loop through each row
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(SENDER_EMAIL, APP_PASSWORD)

    for _, row in df.iterrows():
        due_date = row['Due Date'].strftime('%d-%m-%Y') if not pd.isnull(row['Due Date']) else ""
        if due_date == today_str:
            recipient = row['Email']
            subject = f"Payment Reminder - {row['Agreement Name']}"
            body = f"Dear {row['Name']},\n\n{row['Message']}\n\nRegards,\nAccounts Team"

            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient

            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
            print(f"✅ Reminder sent to {recipient}")
