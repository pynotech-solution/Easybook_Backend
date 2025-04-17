from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from Appointments.models import Appointment
from .payment_service import PaystackService
from .models import Transaction

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_subaccount(request):
    """Set up Paystack subaccount for a business with mobile money"""
    if not request.user.is_business:
        return Response(
            {"error": "Only business users can set up subaccounts"},
            status=status.HTTP_403_FORBIDDEN
        )

    business = request.user
    business_name = request.data.get('business_name')
    phone_number = request.data.get('phone_number')
    mobile_money_network = request.data.get('mobile_money_network')

    # Validate required fields
    if not all([business_name, phone_number, mobile_money_network]):
        return Response(
            {"error": "Missing required fields: business_name, phone_number, and mobile_money_network are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate mobile money network
    valid_networks = ['mtn', 'vodafone', 'airteltigo']
    if mobile_money_network.lower() not in valid_networks:
        return Response(
            {"error": f"Invalid mobile money network. Must be one of: {', '.join(valid_networks)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        paystack_service = PaystackService()
        success = paystack_service.create_subaccount(
            business=business,
            business_name=business_name,
            phone_number=phone_number,
            mobile_money_network=mobile_money_network.lower()  # Convert to lowercase
        )
        
        if success:
            return Response(
                {"message": "Subaccount created successfully"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "Failed to create subaccount"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_payment(request, appointment_id):
    """Initialize payment for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not appointment.pricing:
        return Response(
            {"error": "No pricing set for this appointment"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not appointment.service.business.paystack_subaccount_active:
        return Response(
            {"error": "Business has not set up payment account"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        paystack_service = PaystackService()
        payment_url = paystack_service.initialize_payment(
            appointment=appointment,
            email=request.user.email,
            amount=appointment.pricing.price
        )
        return Response({"payment_url": payment_url})
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def verify_payment(request, appointment_id):
    """Verify payment status after Paystack redirect"""
    reference = request.GET.get('reference')
    if not reference:
        return Response(
            {"error": "No reference provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        paystack_service = PaystackService()
        
        if paystack_service.verify_payment(reference):
            # Update appointment status to confirmed
            appointment.status = Appointment.STATUS_CONFIRMED
            appointment.save()
            return Response({"status": "success"})
        
        # If payment verification fails, update appointment status
        appointment.status = Appointment.STATUS_PAYMENT_FAILED
        appointment.save()
        return Response(
            {"status": "failed"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
