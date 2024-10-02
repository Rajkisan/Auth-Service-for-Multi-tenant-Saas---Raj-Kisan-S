import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_email(to_email, subject, content):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    from_email = EMAIL_USER
    from_password = EMAIL_PASSWORD

    try:
        # Validate recipient email
        validate_email(to_email)
        
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))

        # Connect to the Gmail SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())

        return {'status': 'success', 'message': 'Email sent successfully'}

    except EmailNotValidError as e:
        return {'status': 'error', 'message': str(e)}

    except smtplib.SMTPException as e:
        return {'status': 'error', 'message': f'SMTP error occurred: {str(e)}'}

    except Exception as e:
        return {'status': 'error', 'message': f'An error occurred: {str(e)}'}
