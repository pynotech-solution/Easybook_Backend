from rest_framework import serializers
from .models import ServiceCategory, Service, Pricing

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'

class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    pricing_options = PricingSerializer(many=True, read_only=True)
    
    category_id = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all(), source='category', write_only=True)
    category = ServiceCategorySerializer(read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'business', 'name', 'description', 
            'category', 'category_id', 'pricing_options', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['business', 'created_at', 'updated_at']