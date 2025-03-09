from mailersend import emails
import os
from django.conf import settings
from django.utils import timezone

class MailerSendService:
    def __init__(self):
        self.client = emails.NewEmail()
        self.client.set_mailersend_api_key(os.getenv('MAILERSEND_API_KEY'))
        
    def send_email(self, recipient_email, subject, text):
        try:
            mail_from = {
                "email": settings.DEFAULT_FROM_EMAIL,
                "name": "Notification Service"
            }
            
            recipients = [
                {
                    "email": recipient_email
                }
            ]
            
            response = self.client.send({
                "from": mail_from,
                "to": recipients,
                "subject": subject,
                "text": text
            })
            
            return response.status_code == 202
        except Exception as e:
            print(f"MailerSend Error: {str(e)}")
            return False