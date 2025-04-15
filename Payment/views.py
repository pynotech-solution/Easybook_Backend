from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Payment, ServiceProviderPaystackAccount
from .serializers import (
    PaymentSerializer,
    PaymentInitializeSerializer,
    PaymentVerifySerializer,
    PaymentRefundSerializer,
    ServiceProviderPaystackAccountSerializer,
    ServiceProviderPaystackAccountCreateSerializer
)
from .services import PaystackService
from Appointments.models import Appointment
from django.conf import settings

class ServiceProviderPaystackAccountViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceProviderPaystackAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ServiceProviderPaystackAccount.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_account(self, request):
        serializer = ServiceProviderPaystackAccountCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        paystack_service = PaystackService()
        try:
            result = paystack_service.create_subaccount(
                business_name=serializer.validated_data['business_name'],
                payment_method=serializer.validated_data['payment_method'],
                settlement_bank=serializer.validated_data.get('settlement_bank'),
                account_number=serializer.validated_data.get('account_number'),
                mobile_money_provider=serializer.validated_data.get('mobile_money_provider'),
                mobile_money_number=serializer.validated_data.get('mobile_money_number'),
                percentage_charge=serializer.validated_data['percentage_charge']
            )
            
            if not result['success']:
                return Response(
                    {'error': result['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            account = ServiceProviderPaystackAccount.objects.create(
                user=request.user,
                paystack_subaccount_id=result['data']['subaccount_id'],
                payment_method=serializer.validated_data['payment_method'],
                settlement_bank=serializer.validated_data.get('settlement_bank'),
                account_number=serializer.validated_data.get('account_number'),
                mobile_money_provider=serializer.validated_data.get('mobile_money_provider'),
                mobile_money_number=serializer.validated_data.get('mobile_money_number'),
                is_active=True
            )
            
            return Response(
                ServiceProviderPaystackAccountSerializer(account).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def initialize(self, request):
        serializer = PaymentInitializeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        appointment = get_object_or_404(
            Appointment,
            id=serializer.validated_data['appointment_id']
        )

        # Get service provider's Paystack account if exists
        provider_account = None
        if appointment.service_provider:
            provider_account = ServiceProviderPaystackAccount.objects.filter(
                user=appointment.service_provider,
                is_active=True
            ).first()

        paystack_service = PaystackService(provider_account=provider_account)
        
        try:
            payment_data = paystack_service.initialize_payment(
                email=request.user.email,
                amount=appointment.pricing.price,
                callback_url=serializer.validated_data.get('callback_url')
            )

            payment = Payment.objects.create(
                user=request.user,
                appointment=appointment,
                service_provider=appointment.service_provider,
                pricing=appointment.pricing,
                paystack_reference=payment_data['reference']
            )

            return Response(payment_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def verify(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment = get_object_or_404(
            Payment,
            paystack_reference=serializer.validated_data['reference']
        )

        provider_account = None
        if payment.service_provider:
            provider_account = ServiceProviderPaystackAccount.objects.filter(
                user=payment.service_provider,
                is_active=True
            ).first()

        paystack_service = PaystackService(provider_account=provider_account)
        
        try:
            verification_data = paystack_service.verify_payment(
                serializer.validated_data['reference']
            )
            
            if verification_data['status'] == 'success':
                payment.status = 'completed'
                payment.save()
                
                # Update appointment status
                payment.appointment.status = 'confirmed'
                payment.appointment.save()

            return Response(verification_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        serializer = PaymentRefundSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        provider_account = None
        if payment.service_provider:
            provider_account = ServiceProviderPaystackAccount.objects.filter(
                user=payment.service_provider,
                is_active=True
            ).first()

        paystack_service = PaystackService(provider_account=provider_account)
        
        try:
            refund_data = paystack_service.refund_payment(
                payment.paystack_reference,
                serializer.validated_data.get('reason')
            )
            
            payment.status = 'refunded'
            payment.refund_reason = serializer.validated_data.get('reason')
            payment.save()
            
            return Response(refund_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Use the initialize endpoint to create a payment'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
