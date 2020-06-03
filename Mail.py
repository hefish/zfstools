#!/usr/bin/env python3

from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL, SMTP_SSL_PORT


class SMTP:
    def __init__(self, cfg):
        self._smtp_host = cfg['smtp_host']
        self._smtp_port = SMTP_SSL_PORT if not 'smtp_port' in cfg  else cfg['smtp_port']
        self._smtp_user = cfg['smtp_user']
        self._smtp_pass = cfg['smtp_pass']
        self._from_email = cfg['from_email']
        self._to_email = cfg['to_email']

        self.smtp = SMTP_SSL(self._smtp_host, port=self._smtp_port)
    
    def from_email(self, from_email):
        self._from_email = from_email

    def to_email(self, to_email):
        self._to_email = to_email
    
    def subject(self, subject):
        self._subject = subject
    def content(self, content):
        self._content = content

    def send(self):
        self.smtp.ehlo(self._smtp_host)
        self.smtp.login(self._smtp_user, self._smtp_pass)
        
        msg = MIMEText(self._content, "plain", "UTF-8")
        msg['Subject'] = Header(self._subject, "UTF-8")
        msg['From'] = self._from_email
        msg['To'] = str(self._to_email)
        self.smtp.sendmail(self._from_email, self._to_email, msg.as_string())
        
        self.smtp.quit()


