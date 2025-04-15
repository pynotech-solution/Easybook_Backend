from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "is_customer", "is_business", "phone_number", "address", "profile_picture")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_customer=validated_data.get("is_customer", False),
            is_business=validated_data.get("is_business", False),
            phone_number=validated_data.get("phone_number", ""),
            address=validated_data.get("address", ""),
            profile_picture=validated_data.get("profile_picture", None),
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False) # Allow for updating profile picture
    
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number", "address", "profile_picture")
        read_only_fields = ("email",)
