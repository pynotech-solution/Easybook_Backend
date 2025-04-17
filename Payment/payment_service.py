import requests
from django.conf import settings
from decimal import Decimal
from .models import Transaction, Payout

class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def verify_subaccount(self, subaccount_code):
        """Retrieve and verify a Paystack subaccount by its code"""
        url = f"{self.base_url}/subaccount/{subaccount_code}"
        
        response = requests.get(url, headers=self.headers)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') is True:
            return response_data['data']  # Verified details
        else:
            raise Exception(response_data.get('message', 'Subaccount verification failed'))

    def create_subaccount(self, business, business_name, phone_number, mobile_money_network):
        """Create or verify a Paystack subaccount for a business with mobile money"""
        url = f"{self.base_url}/subaccount"
        
        PLATFORM_FEE = 5.0

        if not business.business_email:
            raise ValueError("Business email is required for subaccount creation")
            
        formatted_phone = ''.join(filter(str.isdigit, phone_number))

        provider_codes = {
            'mtn': 'MTN',
            'vodafone': 'VOD',
            'airteltigo': 'ATL'
        }
        
        network = mobile_money_network.lower()
        if network not in provider_codes:
            raise ValueError(f"Invalid mobile money network. Must be one of: {', '.join(provider_codes.keys())}")

        settlement_bank = provider_codes[network]

        # ✅ PREVENT DUPLICATE CREATION
        if business.paystack_subaccount_code:
            try:
                verified = self.verify_subaccount(business.paystack_subaccount_code)
                if verified.get('active'):
                    business.paystack_subaccount_active = True
                    business.mobile_money_network = mobile_money_network
                    business.save()
                    return True
            except Exception as e:
                # Allow fallthrough to re-create if existing one fails
                pass

        payload = {
            "business_name": business_name,
            "settlement_bank": settlement_bank,
            "account_number": formatted_phone,
            "percentage_charge": PLATFORM_FEE,
            "currency": "GHS",
            "description": business.business_description or f"Business account for {business_name}",
            "primary_contact_email": business.business_email,
            "primary_contact_name": business.get_full_name(),
            "primary_contact_phone": formatted_phone,
            "metadata": {
                "business_id": str(business.id)
            }
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response_data = response.json()

            # ✅ CASE 1: Successfully created
            if response.status_code == 200 and response_data.get('status') is True:
                data = response_data['data']
                subaccount_code = data['subaccount_code']

                # Save new subaccount data
                business.paystack_subaccount_id = data['id']
                business.paystack_subaccount_code = subaccount_code
                business.mobile_money_network = mobile_money_network

                # ✅ Automatically verify and update status
                verified = self.verify_subaccount(subaccount_code)
                business.paystack_subaccount_active = verified.get('active', True)
                business.save()
                return True

            # ✅ CASE 2: Already created
            elif response_data.get('message') == 'Subaccount created':
                data = response_data.get('data', {})
                subaccount_code = data.get('subaccount_code')
                if not subaccount_code:
                    raise Exception("No subaccount code returned by Paystack")

                verified = self.verify_subaccount(subaccount_code)
                business.paystack_subaccount_id = data.get('id')
                business.paystack_subaccount_code = subaccount_code
                business.paystack_subaccount_active = verified.get('active', True)
                business.mobile_money_network = mobile_money_network
                business.save()
                return True

            else:
                error_message = response_data.get('message', 'Unknown error')
                raise Exception(f"Paystack API error: {error_message}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create subaccount: {str(e)}")

    def initialize_payment(self, appointment, email, amount):
        """Initialize a payment and return the payment URL"""
        url = f"{self.base_url}/transaction/initialize"
        callback_url = f"{settings.BASE_URL}/payment/verify/{appointment.id}/"
        
        payload = {
            "email": email,
            "amount": int(amount * 100),  # Paystack expects amount in kobo/pesewas
            "currency": "GHS",
            "callback_url": callback_url,
            "subaccount": appointment.service.business.paystack_subaccount_code,
            "bearer": "subaccount",  # Business pays the transaction fee
            "channels": ["mobile_money"],
            "metadata": {
                "appointment_id": str(appointment.id)
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            # Create transaction record
            Transaction.objects.create(
                appointment=appointment,
                amount=amount,
                paystack_reference=data['data']['reference']
            )
            return data['data']['authorization_url']
        raise Exception("Failed to initialize payment")

    def verify_payment(self, reference):
        """Verify a payment status"""
        url = f"{self.base_url}/transaction/verify/{reference}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            if data['data']['status'] == 'success':
                # Update transaction status
                transaction = Transaction.objects.get(paystack_reference=reference)
                transaction.status = Transaction.STATUS_SUCCESSFUL
                transaction.save()
                
                # Create payout record (now handled automatically by Paystack)
                self._create_payout(transaction)
                return True
        return False

    def _create_payout(self, transaction):
        """Create a payout record for tracking"""
        amount = transaction.amount
        platform_fee = amount * Decimal('0.05')  # 5% platform fee
        business_amount = amount - platform_fee
        
        Payout.objects.create(
            business=transaction.appointment.service.business,
            transaction=transaction,
            amount=business_amount,
            platform_fee=platform_fee,
            status=Payout.STATUS_PROCESSED  # Mark as processed since Paystack handles the split
        )

    def initiate_transfer(self, payout):
        """Initiate transfer to business's mobile money account"""
        url = f"{self.base_url}/transfer"
        
        payload = {
            "source": "balance",
            "amount": int(payout.amount * 100),  # Convert to kobo/pesewas
            "currency": "GHS",
            "recipient": payout.business.paystack_recipient_code,  # Business needs to have this set up
            "reason": f"Payment for appointment {payout.transaction.appointment.id}"
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            payout.paystack_transfer_reference = data['data']['reference']
            payout.status = Payout.STATUS_PROCESSED
            payout.save()
            return True
        return False 