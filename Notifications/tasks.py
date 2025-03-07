from celery import shared_task
from django.utils import timezone
from .models import Notification
from .services import TwilioNotificationService

@shared_task
def send_scheduled_notifications():
    now = timezone.now()
    pending = Notification.objects.filter(
        status='pending',
        scheduled_time__lte=now
    ).select_related('user')
    
    service = TwilioNotificationService()
    
    for notification in pending:
        success = service.send_notification(notification.user, notification.message)
        notification.status = 'sent' if success else 'failed'
        notification.save()