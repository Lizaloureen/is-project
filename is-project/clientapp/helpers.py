
from django.core.mail import EmailMessage
from django.conf import settings


def send_mail(mail_subject,mail_message, mail_to: list = [], cc:list = [], bcc:list=[]):
    # Code to send email
    mail_from = settings.EMAIL_HOST_USER
    email = EmailMessage(mail_subject, mail_message, mail_from, cc, bcc, to=mail_to)
    email.send()
    