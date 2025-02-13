from rest_framework import serializers
from .models import User
from .models import PasswordRecoveryToken
from django.utils import timezone
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                '__all__'
            )



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value

    def create_recovery_token(self, user):
        # Create a recovery token instance
        token_instance = PasswordRecoveryToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(days=1)
        )
        return token_instance.token

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)
