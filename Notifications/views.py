from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification, UserNotificationPreference
from .serializers import NotificationSerializer, UserNotificationPreferenceSerializer
from .services import EmailService
from django.core.exceptions import ObjectDoesNotExist

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        notification = serializer.save(user=self.request.user)
        self._process_notification(notification)

    def _process_notification(self, notification):
        try:
            preference = notification.user.usernotificationpreference
        except ObjectDoesNotExist:
            preference = UserNotificationPreference.objects.create(
                user=notification.user,
                email=notification.user.email,
                email_enabled=True
            )
        
        if preference.email_enabled:
            email_service = EmailService()
            success, message = email_service.send_email(
                preference.email,
                notification.subject,
                notification.message,
                notification.html_message
            )
            notification.status = 'sent' if success else 'failed'
            notification.email_message = message
        else:
            notification.status = 'failed'
        
        notification.save()

    @action(detail=False, methods=['post'])
    def send_test_email(self, request):
        email_service = EmailService()
        success, message = email_service.send_email(
            request.user.email,
            'Test Email',
            'This is a test email from EasyBook.',
            '<h1>Test Email</h1><p>This is a test email from EasyBook.</p>'
        )
        
        if success:
            return Response({'message': 'Test email sent successfully'})
        else:
            return Response(
                {'error': f'Failed to send test email: {message}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserNotificationPreference.objects.all()
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserNotificationPreference.objects.filter(user=self.request.user)