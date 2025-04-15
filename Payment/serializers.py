from rest_framework import serializers
from .models import Payment, ServiceProviderPaystackAccount

class ServiceProviderPaystackAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderPaystackAccount
        fields = [
            'id', 'user', 'paystack_subaccount_id', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ServiceProviderPaystackAccountCreateSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=['bank', 'mobile_money'])
    # Bank account fields
    settlement_bank = serializers.CharField(required=False)
    account_number = serializers.CharField(required=False)
    # Mobile money fields
    mobile_money_provider = serializers.CharField(required=False)
    mobile_money_number = serializers.CharField(required=False)
    percentage_charge = serializers.FloatField()

    def validate(self, data):
        payment_method = data.get('payment_method')
        
        if payment_method == 'bank':
            if not data.get('settlement_bank') or not data.get('account_number'):
                raise serializers.ValidationError("Settlement bank and account number are required for bank payments")
        elif payment_method == 'mobile_money':
            if not data.get('mobile_money_provider') or not data.get('mobile_money_number'):
                raise serializers.ValidationError("Mobile money provider and number are required for mobile money payments")
        
        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'appointment', 'user', 'service_provider', 'amount',
            'currency', 'status', 'paystack_reference', 'payment_date',
            'refund_reason', 'refund_date', 'platform_fee', 'provider_amount'
        ]
        read_only_fields = [
            'id', 'user', 'service_provider', 'status', 'paystack_reference',
            'payment_date', 'refund_date', 'platform_fee', 'provider_amount'
        ]

class PaymentInitializeSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()
    callback_url = serializers.URLField(required=False)

class PaymentVerifySerializer(serializers.Serializer):
    reference = serializers.CharField()

class PaymentRefundSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False) 