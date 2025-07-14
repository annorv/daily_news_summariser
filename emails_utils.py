import smtplib
from email.mime.text import MIMEText
import os

def send_email(subject, body):
    sender = os.getenv("EMAIL_USER")
    recipient = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)
