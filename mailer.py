import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "127.0.0.1"
SMTP_PORT = 1025

SMTP_USER = "vedebech@protonmail.com"
SMTP_PASS = "HD0iVeNsMnTmgHPjiPI4uA"

def send_mail(subject, body_html, receiver):
    print("Mailer sender via ProtonMail Bridge…")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = receiver

    html = f"""
    <html>
      <body style="font-family: Arial; font-size: 18px; line-height: 1.4;">
        <h2 style="margin-bottom: 5px; font-size: 26px;">{subject}</h2>

        {body_html}

        <h3 style="margin-top: 25px; font-size: 20px;">Fradrag</h3>
        <p style="font-size: 16px; color: #444;">
          -20 % på 18 kt<br>
          -20 % på 14 kt<br>
          -20 % på 8 kt
        </p>

        <p style="margin-top: 25px; font-size: 14px; color: #666;">
          Denne rapport genereres automatisk af dit overvågningssystem.
        </p>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print("Mail sendt!")

    except Exception as e:
        print("MAIL FEJL:", e)
