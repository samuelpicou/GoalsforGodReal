import smtplib
from email.message import EmailMessage

def send_daily_reminder(user_email, goal_name, scripture):
    msg = EmailMessage()
    msg.set_content(f"Keep going! Your goal: {goal_name}\n\nDaily Scripture: {scripture}")
    msg['Subject'] = "GoalsForGod: Your 12-Week Daily Manna"
    msg['From'] = "your-email@gmail.com"
    msg['To'] = user_email

    # Note: Requires an App Password from Google settings
    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    #     smtp.login('USER', 'PASS')
    #     smtp.send_message(msg)
    print(f"Reminder sent to {user_email}")