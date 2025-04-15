from rest_framework import serializers
from .models import Notification, UserNotificationPreference
from django.utils import timezone

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'user', 'mailersend_id']
        
    def validate_scheduled_at(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value

class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreference
        fields = ['email_enabled', 'email']
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required")
        return value