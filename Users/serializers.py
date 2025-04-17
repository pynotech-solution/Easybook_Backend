from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    business_email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = (
            "id", "email", "password", "first_name", "last_name", 
            "is_customer", "is_business", "phone_number", "address", 
            "profile_picture", "business_name", "business_description",
            "business_address", "business_phone", "business_email",
            "paystack_subaccount_active", "mobile_money_network"
        )

    def validate(self, data):
        if data.get('is_business'):
            # For business users, set business_email to their email
            data['business_email'] = data.get('email')
        return data

    def to_representation(self, instance):
        """Customize the representation based on user type"""
        data = super().to_representation(instance)
        if not instance.is_business:
            # Remove business-related fields for non-business users
            data.pop('business_name', None)
            data.pop('business_description', None)
            data.pop('business_address', None)
            data.pop('business_phone', None)
            data.pop('business_email', None)
            data.pop('paystack_subaccount_active', None)
            data.pop('mobile_money_network', None)
        return data

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
            business_name=validated_data.get("business_name", ""),
            business_description=validated_data.get("business_description", ""),
            business_address=validated_data.get("business_address", ""),
            business_phone=validated_data.get("business_phone", ""),
            business_email=validated_data.get("email") if validated_data.get("is_business") else validated_data.get("business_email", ""),
            mobile_money_network=validated_data.get("mobile_money_network", None)
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False) # Allow for updating profile picture
    business_email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name", "phone_number", 
            "address", "profile_picture", "business_name", "business_description",
            "business_address", "business_phone", "business_email",
            "paystack_subaccount_active", "mobile_money_network"
        )
        read_only_fields = ("email", "paystack_subaccount_active")

    def validate(self, data):
        if self.instance.is_business:
            # For business users, business_email is always their email
            data['business_email'] = self.instance.email
        return data

    def to_representation(self, instance):
        """Customize the representation based on user type"""
        data = super().to_representation(instance)
        if not instance.is_business:
            # Remove business-related fields for non-business users
            data.pop('business_name', None)
            data.pop('business_description', None)
            data.pop('business_address', None)
            data.pop('business_phone', None)
            data.pop('business_email', None)
            data.pop('paystack_subaccount_active', None)
            data.pop('mobile_money_network', None)
        return data
