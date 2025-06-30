from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

def send_student_email(to_email, student_name, default_username, default_password):
    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=to_email,
        subject='?? Student Portal Login Credentials',
        html_content=f"""
        <p>Dear {student_name},</p>
        <p>You have been <strong>approved</strong> for admission.</p>
        <p>Use the following credentials to log in to the Student Portal:</p>
        <ul>
            <li><strong>Login URL:</strong> <a href="{settings.LOGIN_URL}">{settings.LOGIN_URL}</a></li>
            <li><strong>Username:</strong> {default_username}</li>
            <li><strong>Password:</strong> {default_password}</li>
        </ul>
        <p>?? You must change your username and password after logging in for the first time.</p>
        <p>Regards,<br>Admissions Team</p>
        """
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        print(f"? Email sent to {to_email}")
    except Exception as e:
        print(f"? Failed to send email to {to_email}: {str(e)}")


from django.utils.timezone import localtime, now

def get_indian_time():
    return localtime(now())

import random
import string

def generate_student_credentials(existing_userids=None):
    if existing_userids is None:
        existing_userids = set()
    # Generate a unique student_userid
    while True:
        userid = 'STU' + ''.join(random.choices(string.digits, k=5))
        if userid not in existing_userids:
            break
    # Generate a random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return userid, password
