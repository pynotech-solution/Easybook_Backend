from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets, filters, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from .models import Service, ServiceCategory, Pricing
from .serializers import ServiceSerializer, ServiceCategorySerializer, PricingSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]


    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'business']  # Allow filtering by category and business
    ordering_fields = ['created_at', 'name']     # Allow ordering by creation date and name
    search_fields = ['name', 'description']        # Allow searching by name and description

    def perform_create(self, serializer):
        serializer.save(business=self.request.user)

class ServiceCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PricingListCreateView(generics.ListCreateAPIView):
    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service = serializer.validated_data.get('service')
        if service.business != self.request.user:
            raise PermissionDenied("You are not allowed to add pricing for this service.")
        serializer.save()

