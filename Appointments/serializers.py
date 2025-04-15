from rest_framework import serializers
from .models import TimeSlot, Appointment
from Services.models import Pricing

class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = ['id', 'price', 'currency', 'description']
        read_only_fields = ['id']

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'

class AppointmentCreateSerializer(serializers.ModelSerializer):
    pricing_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'timeslot', 'service', 'pricing_id', 'status']
        read_only_fields = ['id', 'status']

    def validate(self, data):
        # Validate pricing belongs to the selected service
        pricing = Pricing.objects.filter(
            id=data['pricing_id'],
            service=data['service']
        ).first()
        
        if not pricing:
            raise serializers.ValidationError("Invalid pricing option for the selected service")
        
        return data

    def create(self, validated_data):
        pricing_id = validated_data.pop('pricing_id')
        pricing = Pricing.objects.get(id=pricing_id)
        
        # Remove user from validated_data if it exists
        validated_data.pop('user', None)
        
        appointment = Appointment.objects.create(
            **validated_data,
            pricing=pricing,
            user=self.context['request'].user
        )
        
        return appointment

class AppointmentSerializer(serializers.ModelSerializer):
    pricing = PricingSerializer(read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
