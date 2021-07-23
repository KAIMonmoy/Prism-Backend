import smtplib
from email.message import EmailMessage
from django.conf import settings


def send_email(subject, message, recipients):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        mail = EmailMessage()
        mail['From'] = settings.EMAIL_HOST_USER
        mail['To'] = recipients
        mail['Subject'] = subject
        mail.set_content(subject + "\n" + message)
        mail.add_alternative("""\
            <!DOCTYPE html>
            <html lang="en">
            <body style="background-color: #ffffff;">
            """ + message + """
            </body>
            </html>
            """, subtype='html')
        smtp.send_message(mail)
