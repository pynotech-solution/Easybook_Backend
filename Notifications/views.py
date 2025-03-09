from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Notification, UserNotificationPreference
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer, UserNotificationPreferenceSerializer
from .services import MailerSendService

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        notification = serializer.save(user=self.request.user)
        self._process_notification(notification)

    def _process_notification(self, notification):
        try:
            preference = notification.user.usernotificationpreference
            
            if preference.email_enabled:
                mailer = MailerSendService()
                success = mailer.send_email(
                    recipient_email=preference.email,
                    subject=notification.subject,
                    text=notification.message
                )
                notification.status = 'sent' if success else 'failed'
            else:
                notification.status = 'failed'
                
        except UserNotificationPreference.DoesNotExist:
            notification.status = 'failed'
        finally:
            notification.save()

class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserNotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)