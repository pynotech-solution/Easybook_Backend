import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Payment, ServiceProviderPaystackAccount

class PaystackService:
    def __init__(self, provider_account=None):
        self.provider_account = provider_account
        if provider_account:
            self.secret_key = provider_account.paystack_secret_key
            self.public_key = provider_account.paystack_public_key
        else:
            self.secret_key = settings.PAYSTACK_SECRET_KEY
            self.public_key = settings.PAYSTACK_PUBLIC_KEY
            
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def create_subaccount(self, business_name, payment_method, settlement_bank=None, account_number=None, 
                         mobile_money_provider=None, mobile_money_number=None, percentage_charge=None):
        """
        Create a subaccount for a service provider
        """
        try:
            url = f"{self.base_url}/subaccount"
            payload = {
                "business_name": business_name,
                "percentage_charge": percentage_charge
            }

            if payment_method == 'bank':
                payload.update({
                    "settlement_bank": settlement_bank,
                    "account_number": account_number
                })
            elif payment_method == 'mobile_money':
                payload.update({
                    "mobile_money_provider": mobile_money_provider,
                    "mobile_money_number": mobile_money_number
                })

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get('status'):
                return {
                    'success': True,
                    'data': {
                        'subaccount_id': data['data']['subaccount_id'],
                        'subaccount_code': data['data']['subaccount_code']
                    }
                }
            return {
                'success': False,
                'message': data.get('message', 'Failed to create subaccount')
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': str(e)
            }

    def initialize_payment(self, email, amount, appointment_id, callback_url=None):
        """
        Initialize a payment transaction with Paystack
        """
        try:
            url = f"{self.base_url}/transaction/initialize"
            payload = {
                "email": email,
                "amount": int(amount * 100),  # Convert to kobo
                "callback_url": callback_url,
                "metadata": {
                    "appointment_id": appointment_id
                }
            }

            # Add subaccount if provider account exists
            if self.provider_account:
                payload["subaccount"] = self.provider_account.paystack_subaccount_id

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get('status'):
                return {
                    'success': True,
                    'data': {
                        'authorization_url': data['data']['authorization_url'],
                        'access_code': data['data']['access_code'],
                        'reference': data['data']['reference']
                    }
                }
            return {
                'success': False,
                'message': data.get('message', 'Failed to initialize payment')
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': str(e)
            }

    def verify_payment(self, reference):
        """
        Verify a payment transaction with Paystack
        """
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if data.get('status'):
                transaction = data['data']
                return {
                    'success': True,
                    'data': {
                        'status': transaction['status'],
                        'amount': float(transaction['amount']) / 100,  # Convert from kobo
                        'reference': transaction['reference'],
                        'paid_at': transaction.get('paid_at'),
                        'metadata': transaction.get('metadata', {}),
                        'subaccount': transaction.get('subaccount', {})
                    }
                }
            return {
                'success': False,
                'message': data.get('message', 'Failed to verify payment')
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': str(e)
            }

    def create_refund(self, payment, reason=None):
        """
        Create a refund for a payment
        """
        try:
            if not payment.paystack_reference:
                raise ValidationError("Payment reference not found")

            url = f"{self.base_url}/refund"
            payload = {
                "transaction": payment.paystack_reference,
                "amount": int(payment.amount * 100),  # Convert to kobo
                "reason": reason
            }

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get('status'):
                return {
                    'success': True,
                    'data': {
                        'reference': data['data']['reference'],
                        'status': data['data']['status']
                    }
                }
            return {
                'success': False,
                'message': data.get('message', 'Failed to create refund')
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': str(e)
            }

    def verify_webhook_signature(self, payload, signature):
        """
        Verify the signature of a webhook payload
        """
        import hmac
        import hashlib
        import json

        if not settings.PAYSTACK_WEBHOOK_SECRET:
            raise ValidationError("Webhook secret not configured")

        expected_signature = hmac.new(
            settings.PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
            json.dumps(payload).encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature) 