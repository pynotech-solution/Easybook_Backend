from django.shortcuts import render

# Create your views here.

from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import TimeSlot, Appointment
from .serializers import TimeSlotSerializer, AppointmentSerializer, TimeSlotSerializer, AppointmentCreateSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from Payment.payment_service import PaystackService
from django.shortcuts import get_object_or_404



class AvailableTimeSlotListView(generics.ListAPIView):
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Exclude time slots that have an appointment with status Pending or Confirmed.
        return TimeSlot.objects.exclude(
            appointments__status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
        )
    


class AppointmentCreateView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        timeslot = serializer.validated_data['timeslot']
        if Appointment.objects.filter(
                timeslot=timeslot, 
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
            ).exists():
            raise ValidationError("This timeslot is already booked.")
        
        # Create appointment with payment pending status
        appointment = serializer.save(
            user=self.request.user,
            status=Appointment.STATUS_PAYMENT_PENDING
        )
        
        try:
            # Initialize payment
            paystack_service = PaystackService()
            payment_url = paystack_service.initialize_payment(
                appointment=appointment,
                email=self.request.user.email,
                amount=appointment.pricing.price
            )
            
            # Store payment URL in the response
            self.payment_url = payment_url
            
        except Exception as e:
            appointment.status = Appointment.STATUS_PAYMENT_FAILED
            appointment.save()
            raise ValidationError(f"Payment initialization failed: {str(e)}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if hasattr(self, 'payment_url'):
            response.data['payment_url'] = self.payment_url
        return response


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)
    

class TimeSlotCreateView(generics.CreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create appointment with payment pending status
        appointment = serializer.save(status=Appointment.STATUS_PAYMENT_PENDING)
        
        try:
            # Initialize payment
            paystack_service = PaystackService()
            payment_url = paystack_service.initialize_payment(
                appointment=appointment,
                email=request.user.email,
                amount=appointment.pricing.price
            )
            
            # Return appointment data with payment URL
            response_data = serializer.data
            response_data['payment_url'] = payment_url
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If payment initialization fails, update appointment status
            appointment.status = Appointment.STATUS_PAYMENT_FAILED
            appointment.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def payment_status(self, request, pk=None):
        appointment = self.get_object()
        return Response({
            'status': appointment.status,
            'payment_url': request.build_absolute_uri(f'/api/payment/appointments/{appointment.id}/initialize/')
        })

