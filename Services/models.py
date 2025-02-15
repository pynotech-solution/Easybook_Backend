from django.db import models
import uuid
from django.conf import settings

class ServiceCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    business = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Pricing(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='pricing_options')
    price = models.DecimalField(max_digits=100, decimal_places=2)
    currency = models.CharField(max_length=10, default='GH₵')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.price} {self.currency}"