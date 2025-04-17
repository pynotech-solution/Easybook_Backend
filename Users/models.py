from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)  # Ensure user is active by default

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)  # Superuser should always be active

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    is_customer = models.BooleanField(default=False)
    is_business = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    paystack_subaccount_id = models.CharField(max_length=100, null=True, blank=True)
    paystack_subaccount_code = models.CharField(max_length=100, null=True, blank=True)
    paystack_subaccount_active = models.BooleanField(default=False)
    mobile_money_network = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('MTN', 'MTN Mobile Money'),
            ('VODAFONE', 'Vodafone Cash'),
            ('AIRTELTIGO', 'AirtelTigo Money')
        ]
    )
    
    # Business specific fields
    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_description = models.TextField(null=True, blank=True)
    business_address = models.TextField(null=True, blank=True)
    business_phone = models.CharField(max_length=20, null=True, blank=True)
    business_email = models.EmailField(null=True, blank=True)

    USERNAME_FIELD = "email"  # Use email instead of username for authentication
    REQUIRED_FIELDS = ["first_name", "last_name"]  # Make first and last name required

    objects = CustomUserManager()  # Use custom manager

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
