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
from Users.views import CreateUser, LoginView, ProfileView, PasswordResetRequestView, PasswordResetConfirmView
from rest_framework.authtoken.views import obtain_auth_token
from Services.views import ServiceViewSet, ServiceCategoryListCreateView,PricingListCreateView


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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    #Users api endpoints
    path('register/', CreateUser.as_view(), name='create_user'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    #Services api endpoints
    path('services/', service_list, name='service-list'),
    path('services/<int:pk>/', service_detail, name='service-detail'),
    path('services/categories/', ServiceCategoryListCreateView.as_view(), name='service-category-list-create'),
    path('pricing/', PricingListCreateView.as_view(), name='pricing-list-create'),


]
