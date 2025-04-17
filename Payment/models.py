from django.db import models
from django.conf import settings
from Appointments.models import Appointment

class Transaction(models.Model):
    STATUS_PENDING = 'P'
    STATUS_SUCCESSFUL = 'S'
    STATUS_FAILED = 'F'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESSFUL, 'Successful'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction for {self.appointment} - {self.amount}"

class Payout(models.Model):
    STATUS_PENDING = 'P'
    STATUS_PROCESSED = 'S'
    STATUS_FAILED = 'F'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSED, 'Processed'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    business = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount after platform fee
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)  # 5% of transaction amount
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    paystack_transfer_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payout for {self.business} - {self.amount}"
