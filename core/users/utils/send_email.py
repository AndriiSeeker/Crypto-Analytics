import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import environ

from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


def send_email(message, to_email, ) -> None:
    with smtplib.SMTP_SSL(env('EMAIL_HOST'), env('EMAIL_HOST_PORT')) as server:
        try:
            from_email = env('EMAIL_HOST_USER')
            from_email_password = env('EMAIL_HOST_PASSWORD')
            server.login(from_email, from_email_password)
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = 'Confirm registration'

            msg.attach(MIMEText(message, 'html'))

            print(msg)
            server.send_message(msg)
        except Exception as err:
            print(err)


print(send_email("Testing", "andriy.svitelskyi@gmail.com"))
