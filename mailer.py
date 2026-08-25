import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


SMTP_HOST = "127.0.0.1"
SMTP_PORT = 1025
SMTP_USER = os.getenv("BRIDGE_USERNAME")
SMTP_PASS = os.getenv("BRIDGE_PASSWORD")

def send_mail(subject, body_html, receiver):
    if not all((SMTP_USER, SMTP_PASS, receiver)):
        raise ValueError("Mailkonfigurationen mangler BRIDGE_USERNAME, BRIDGE_PASSWORD eller modtager.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = receiver

    # HTML‑delen
    html_part = MIMEText(body_html, "html")
    msg.attach(html_part)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
