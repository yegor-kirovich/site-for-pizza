import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(email, title, text):
    addr_from = os.getenv('FROM')
    password = os.getenv('PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = email
    msg['Subject'] = title

    msg.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP_SSL(os.getenv('HOST'), os.getenv('PORT_MAIL'))
    server.login(addr_from, password)

    server.send_message(msg)
    server.quit()
    return True
