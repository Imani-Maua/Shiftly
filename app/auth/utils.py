import hashlib
import string
import secrets
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
SECRET_KEY = os.getenv("KEY")
algorithm = "HS256"
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 2525))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


def hash_password(password: str) -> str:
    prehash = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(prehash)


def verify_password(password: str, hash: str) -> bool:
    prehash = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.verify(prehash, hash)

def generate_temporary_password():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    temporary = ''.join(secrets.choice(alphabet) for _ in range(12))
    print(temporary)
    return temporary


def send_email(to_email:str, subject: str, body: str):

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise



