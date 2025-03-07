from rest_framework import serializers
from .models import Notification, NotificationPreference
from django.utils import timezone

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 
            'message', 
            'scheduled_time', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']
        extra_kwargs = {
            'scheduled_time': {'required': True}
        }

    def validate_scheduled_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future"
            )
        return value

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'phone',
            'email',
            'fcm_token',
            'receive_sms',
            'receive_email',
            'receive_push'
        ]
        extra_kwargs = {
            'phone': {'required': False},
            'email': {'required': False},
            'fcm_token': {'required': False}
        }

    def validate_phone(self, value):
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must include country code (e.g. +1...)"
            )
        return value