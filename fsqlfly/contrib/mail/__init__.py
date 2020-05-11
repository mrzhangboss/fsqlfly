import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date


class MailSender:
    def __init__(self, mail_host: str, mail_user: str, mail_password: str, mail_receivers: str):
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_password = mail_password
        self.mail_receivers = mail_receivers.split(',')

    def send_email(self, title: str, content: str):
        today = date.today()
        title = f'{today}{title}'

        message = MIMEMultipart()
        message['From'] = "{}".format(self.mail_user)
        message['To'] = ",".join(self.mail_receivers)
        message['Subject'] = title
        txt = MIMEText(content, 'plain', 'utf-8')
        message.attach(txt)

        try:
            smtp_obj = smtplib.SMTP_SSL(self.mail_host, 465)
            smtp_obj.login(self.mail_user, self.mail_password)
            smtp_obj.sendmail(self.mail_user, self.mail_receivers, message.as_string())
            return "{} mail has been send successfully.".format(str(datetime.now())[:19])
        except smtplib.SMTPException as e:
            return str(e)


class MailHelper:
    _sender: MailSender = None

    @classmethod
    def init(cls):
        from fsqlfly.settings import (FSQLFLY_MAIL_HOST, FSQLFLY_MAIL_USER, FSQLFLY_MAIL_PASSWORD,
                                      FSQLFLY_MAIL_RECEIVERS)
        cls._sender = MailSender(FSQLFLY_MAIL_HOST,
                                 FSQLFLY_MAIL_USER,
                                 FSQLFLY_MAIL_PASSWORD,
                                 FSQLFLY_MAIL_RECEIVERS)

    @classmethod
    def send(cls, title: str, content: str):
        if cls._sender is None:
            cls.init()

        cls._sender.send_email(title, content)
