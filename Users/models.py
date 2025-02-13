from django.db import models
import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser


# Create your models here.

class User(AbstractBaseUser):
    Roles = {
        'A': 'Admin',
        'C': 'Customer',
        'B': 'Business',
    }

    Languages = {
        'E': 'English',
        'F': 'French',
        'S': 'Spanish',
    }
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=1000)
    last_name = models.CharField(max_length=1000)
    other_names = models.CharField(max_length=1000)
    email = models.EmailField(max_length=1000, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=1000, default='')
    role = models.CharField(max_length=1, choices=[(Roles, Roles) for Roles in Roles])
    language = models.CharField(max_length=1, choices=[(Languages, Languages) for Languages in Languages])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'other_names']

    def __str__(self):
        return self.email

    
class PasswordRecoveryToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recovery_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(days=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recovery token for {self.user.id}"
