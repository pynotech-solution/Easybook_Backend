from django.conf import settings
import logging
from sib_api_v3_sdk import ApiClient, Configuration, SendSmtpEmail, TransactionalEmailsApi

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        config = Configuration()
        config.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_client = ApiClient(configuration=config)
        self.api_instance = TransactionalEmailsApi(self.api_client)

    def send_email(self, recipient_email, subject, text_content, html_content=None):
        """
        Send email using Brevo's API
        Returns: (success: bool, message: str)
        """
        try:
            logger.info(f"Attempting to send email to {recipient_email}")
            
            sender = {"name": settings.EMAIL_SENDER_NAME, "email": settings.DEFAULT_FROM_EMAIL}
            to = [{"email": recipient_email}]
            
            send_smtp_email = SendSmtpEmail(
                to=to,
                html_content=html_content,
                text_content=text_content,
                subject=subject,
                sender=sender
            )
            
            result = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully to {recipient_email}")
            return True, 'Email sent successfully'
        except Exception as e:
            logger.error(f"Email Error: {str(e)}")
            return False, str(e)