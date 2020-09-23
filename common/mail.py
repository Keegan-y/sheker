import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import MAIL_HOST, MAIL_PORT, MAIL_SENDER, MAIL_CODE, WEB_SERVER_DOMAIN, RESET_PASSOWD_PAGE_URL


def login_mail_server():
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(MAIL_SENDER, MAIL_CODE)
        # TODO: Send email here
        return server
    except Exception as e:
        # Print any error messages to stdout
        print(e)


def create_ressetpassword_mail(receiver_email, token):
    message = MIMEMultipart("alternative")

    message["Subject"] = "密码重置"
    message["From"] = MAIL_SENDER
    message["To"] = receiver_email
    html = f"""\
    <html>
    <body>
        <p>Hi,<br>
        请点击一下连接重置密码: <strong>{WEB_SERVER_DOMAIN}{RESET_PASSOWD_PAGE_URL}?token={token}<strong> <br/>
        </p>
        <p>
        <strong>连接有效时间 2 小时!<strong>
        </p>
    </body>
    </html>
    """
    part = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part)
    return message.as_string()


def create_code_mail(receiver_email, code):
    message = MIMEMultipart("alternative")

    message["Subject"] = "邮箱验证码"
    message["From"] = MAIL_SENDER
    message["To"] = receiver_email
    html = f"""\
    <html>
    <body>
        <p>Hi,<br>
        本次的邮箱验证码是: <strong>{code}<strong>
        </p>
        <p>
        <strong>验证码有效时间 5 分钟!<strong>
        </p>
    </body>
    </html>
    """
    part = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part)
    return message.as_string()


def send_mail_code(receiver_email, code):
    server = login_mail_server()
    message = create_code_mail(receiver_email, code)
    server.sendmail(MAIL_SENDER, receiver_email, message)


def send_mail_reset(receiver_email, token):
    server = login_mail_server()
    message = create_ressetpassword_mail(receiver_email, token)
    server.sendmail(MAIL_SENDER, receiver_email, message)
