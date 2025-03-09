from django.db import models
from django.contrib.auth.models import User

class UserNotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_enabled = models.BooleanField(default=True)
    email = models.EmailField()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('reminder', 'Reminder'),
        ('confirmation', 'Confirmation'),
        ('update', 'Update'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    scheduled_at = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)