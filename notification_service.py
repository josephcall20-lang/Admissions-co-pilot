from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class NotificationService:
    def __init__(self):
        # Email configuration (placeholder - would use real SMTP settings)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', 'admissions@oasisofhealing.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD', 'password')
        
        # SMS configuration (placeholder - would use Twilio or similar)
        self.sms_enabled = os.getenv('SMS_ENABLED', 'false').lower() == 'true'
    
    def send_email(self, to_email, subject, body, template_vars=None):
        """Send an email notification"""
        try:
            # Replace template variables
            if template_vars:
                for key, value in template_vars.items():
                    body = body.replace(f'{{{key}}}', str(value))
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # In a real implementation, this would actually send the email
            print(f"EMAIL SENT TO: {to_email}")
            print(f"SUBJECT: {subject}")
            print(f"BODY: {body}")
            print("---")
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_sms(self, to_phone, message, template_vars=None):
        """Send an SMS notification"""
        try:
            # Replace template variables
            if template_vars:
                for key, value in template_vars.items():
                    message = message.replace(f'{{{key}}}', str(value))
