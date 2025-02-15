from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import TimeSlot, Appointment
from .serializers import TimeSlotSerializer, AppointmentSerializer, TimeSlotSerializer
from rest_framework.exceptions import ValidationError



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
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        timeslot = serializer.validated_data['timeslot']
        if Appointment.objects.filter(
                timeslot=timeslot, 
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
            ).exists():
            raise ValidationError("This timeslot is already booked.")
        serializer.save(user=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)
    

class TimeSlotCreateView(generics.CreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 

