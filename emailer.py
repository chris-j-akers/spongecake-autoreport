import smtplib
import ssl
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email.mime.base import MIMEBase 
from email import encoders 

# ===============================================
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
GMAIL_PORT = 465
GMAIL_SERVER = 'smtp.gmail.com'
# ===============================================

class Email:
    '''
    Build and send an email from a Gmail Account with images and attachments.

    Requires the following Environment Variables:

        GMAIL_USER | Email account username
        GMAIL_PASSWORD | The password (in plain text)

    WARNING: This class is not particularly safe. It uses plain text usernames
    and passwords stored in an environment variable to connect to a Gmail
    account and send emails. Gmail does not allow this by default and you will
    have to enable 'Less Safe Apps' mode, first. It is recommended that you do
    not use your own, personal (or business!) Gmail account with this class, but
    set-up a dummy account that is completely separate from your own.

    This module has been included to provide an easy way to email the report to
    an address once generated.

    Frankly, it probably shouldn't be used :)
    '''

    def __init__(self):
        self.msg = MIMEMultipart('mixed')

    def add_image(self, img_path, img_id):
        '''
        Add an image file to the email.

        Parameters:

        img_path : Full path to the image file
        img_id : Unique Id for the image that MIME can use to identify it
        '''
        with open(img_path, 'rb') as img_file:
            mime_image = MIMEImage(img_file.read(), name=img_id)
            mime_image.add_header('Content-ID', '<{0}>'.format(img_id))
            self.msg.attach(mime_image)

    def add_body(self, html):
        '''
        Add HTML text to the email.

        Parameters:

        html : The text that forms the body of the email in HTML format
        '''
        msg_html = MIMEText(html, 'html', 'utf-8')
        self.msg.attach(msg_html)

    def send(self, subject, recipients):
        '''
        Send the email to a list of recipients.

        Parameters:

        subject : Subject of the email
        recipients: A Python list of email addresses 
        '''
        logging.getLogger(__name__)
        context = ssl.create_default_context()
        self.msg['Subject'] = subject
        with smtplib.SMTP_SSL(GMAIL_SERVER, GMAIL_PORT, context=context) as mail_server:
            mail_server.login(GMAIL_USER, GMAIL_PASSWORD)
            mail_server.sendmail(GMAIL_USER, recipients, self.msg.as_string())

    def add_attachment(self, attachment_path):
        '''
        Add an attachment to the email.

        Parameters:

        attachment_path : Full path to the attachment.
        '''
        attachment = open(attachment_path, 'rb')
        base = MIMEBase('application', 'octet-stream')
        base.set_payload((attachment).read()) 
        encoders.encode_base64(base) 
        base.add_header('Content-Disposition', "attachment; filename={0}".format(os.path.basename(attachment_path)))
        
        self.msg.attach(base) 
