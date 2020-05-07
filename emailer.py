import smtplib
import ssl
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header

# ===============================================
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
GMAIL_PORT = 465
GMAIL_SERVER = 'smtp.gmail.com'
# ===============================================

class email:

    def __init__(self):
        self.msg = MIMEMultipart('mixed')

    def add_image(self, img_path, img_id):
        with open(img_path, 'rb') as img_file:
            mime_image = MIMEImage(img_file.read(), name=img_id)
            mime_image.add_header('Content-ID', '<{0}>'.format(img_id))
            self.msg.attach(mime_image)


    def add_body(self, html):
        msg_html = MIMEText(html, 'html', 'utf-8')
        self.msg.attach(msg_html)


    def send(self, subject, recipients):
        logging.getLogger(__name__)
        context = ssl.create_default_context()
        self.msg['Subject'] = subject
        with smtplib.SMTP_SSL(GMAIL_SERVER, GMAIL_PORT, context=context) as mail_server:
            mail_server.login(GMAIL_USER, GMAIL_PASSWORD)
            mail_server.sendmail(GMAIL_USER, recipients, self.msg.as_string())
