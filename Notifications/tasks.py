from celery import shared_task
from django.utils import timezone
from .models import Notification
from .services import MailerSendService

@shared_task
def process_scheduled_notifications():
    now = timezone.now()
    pending_notifications = Notification.objects.filter(
        status='pending',
        scheduled_at__lte=now
    ).select_related('user__usernotificationpreference')
    
    mailer = MailerSendService()
    
    for notification in pending_notifications:
        try:
            if notification.user.usernotificationpreference.email_enabled:
                success = mailer.send_email(
                    notification.user.usernotificationpreference.email,
                    notification.subject,
                    notification.message
                )
                notification.status = 'sent' if success else 'failed'
            else:
                notification.status = 'failed'
        except Exception as e:
            notification.status = 'failed'
        finally:
            notification.save()