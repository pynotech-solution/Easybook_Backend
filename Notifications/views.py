from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Notification, NotificationPreference
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from .services import TwilioNotificationService

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def send_test(self, request):
        service = TwilioNotificationService()
        message = request.data.get('message', 'Test notification')
        
        success = service.send_notification(
            request.user,
            message
        )
        
        return Response({
            'success': success,
            'message': message
        }, status=status.HTTP_200_OK)

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)