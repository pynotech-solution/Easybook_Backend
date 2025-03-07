from django.db import models
from django.contrib.auth.models import User
from Users.models import User

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fcm_token = models.CharField(max_length=255, blank=True)
    receive_sms = models.BooleanField(default=False)
    receive_email = models.BooleanField(default=False)
    receive_push = models.BooleanField(default=False)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'), 
            ('sent', 'Sent'), 
            ('failed', 'Failed')
            ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)