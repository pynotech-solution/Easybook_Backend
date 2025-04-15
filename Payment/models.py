from django.db import models
from Appointments.models import Appointment
from django.conf import settings

class ServiceProviderPaystackAccount(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('bank', 'Bank Account'),
        ('mobile_money', 'Mobile Money')
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='paystack_account')
    paystack_subaccount_id = models.CharField(max_length=100, unique=True)
    paystack_secret_key = models.CharField(max_length=100)
    paystack_public_key = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    # Bank account fields
    settlement_bank = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=20, null=True, blank=True)
    # Mobile money fields
    mobile_money_provider = models.CharField(max_length=50, null=True, blank=True)  # e.g., MTN, Airtel, etc.
    mobile_money_number = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Provider Paystack Account'
        verbose_name_plural = 'Service Provider Paystack Accounts'

    def __str__(self):
        return f"{self.user.email}'s Paystack Account"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_made')
    service_provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_received')
    pricing = models.ForeignKey('Services.Pricing', on_delete=models.CASCADE, related_name='payments')
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    paystack_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    paystack_access_code = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)
    refund_reason = models.TextField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provider_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"Payment {self.paystack_reference} - {self.pricing.price} {self.pricing.currency}"

    @property
    def amount(self):
        return self.pricing.price

    @property
    def currency(self):
        return self.pricing.currency

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            # Calculate platform fee (e.g., 5% of the total amount)
            self.platform_fee = self.pricing.price * 0.05
            # Calculate provider amount (total amount minus platform fee)
            self.provider_amount = self.pricing.price - self.platform_fee
        super().save(*args, **kwargs)
