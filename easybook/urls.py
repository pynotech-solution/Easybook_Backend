"""
URL configuration for easybook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from users.views import RegisterView, LoginView, RefreshTokenView, ProfileView
from django_rest_passwordreset.views import ResetPasswordRequestToken, ResetPasswordConfirm
from Services.views import ServiceViewSet, ServiceCategoryListCreateView,PricingListCreateView
from Appointments.views import AvailableTimeSlotListView, AppointmentCreateView, AppointmentDetailView, TimeSlotCreateView
from Payment.views import PaymentViewSet, ServiceProviderPaystackAccountViewSet
from Payment.webhooks import paystack_webhook

from rest_framework import routers
from Notifications.views import NotificationViewSet, UserNotificationPreferenceViewSet

notification_list = NotificationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

notification_detail = NotificationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

preference_detail = UserNotificationPreferenceViewSet.as_view({
    'post': 'create',
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update'
})

    

service_list = ServiceViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

service_detail = ServiceViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Define API documentation metadata
schema_view = get_schema_view(
    openapi.Info(
        title="EasyBook API",
        default_version="v1",
        description="API documentation for the EasyBook application.",
        terms_of_service="https://www.easybook.com/terms/",
        contact=openapi.Contact(email="support@easybook.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

# Payment router setup
payment_router = routers.DefaultRouter()
payment_router.register(r'payments', PaymentViewSet, basename='payment')
payment_router.register(r'provider-accounts', ServiceProviderPaystackAccountViewSet, basename='provider-account')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    #Users api endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/', ResetPasswordRequestToken.as_view(), name='password-reset'),
    path('password-reset/confirm/', ResetPasswordConfirm.as_view(), name='password-rese-confirm'),

    #Services api endpoints
    path('services/', service_list, name='service-list'),
    path('services/<int:pk>/', service_detail, name='service-detail'),
    path('services/categories/', ServiceCategoryListCreateView.as_view(), name='service-category-list-create'),
    path('pricing/', PricingListCreateView.as_view(), name='pricing-list-create'),

    #Appointments api endpoints
    path('timeslots/get', AvailableTimeSlotListView.as_view(), name='available-timeslots'),
    path('appointments/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<uuid:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('timeslots/create', TimeSlotCreateView.as_view(), name='timeslot-create'),

    #Notifications api endpoints
    path('notifications/', notification_list, name='notification-list'),
    path('notifications/<int:pk>/', notification_detail, name='notification-detail'),
    path('notifications/preferences/', preference_detail, name='preference-detail'),

    # Payment api endpoints
    path('payments/', include(payment_router.urls)),
    path('payments/initialize/', PaymentViewSet.as_view({'post': 'initialize'}), name='payment-initialize'),
    path('payments/verify/', PaymentViewSet.as_view({'post': 'verify'}), name='payment-verify'),
    path('payments/refund/<int:pk>/', PaymentViewSet.as_view({'post': 'refund'}), name='payment-refund'),
    path('payments/webhook/', paystack_webhook, name='paystack-webhook'),

    # Swagger UI (interactive API documentation)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

