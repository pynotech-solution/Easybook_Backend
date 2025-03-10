from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import PasswordRecoveryToken
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import UserSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .models import User



class CreateUser(APIView):

    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 
            user.set_password(request.data['password'])
            user.save()           
            token, created = Token.objects.get_or_create(user=user)
            response_data = serializer.data
            response_data['token'] = token.key 
            return Response(response_data)
        return Response(serializer.errors)  



class PasswordResetRequestView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        token = serializer.create_recovery_token(user)
        return Response({'detail': 'Password reset email sent.'})

class PasswordResetConfirmView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            recovery_instance = PasswordRecoveryToken.objects.get(token=token)
        except PasswordRecoveryToken.DoesNotExist:
            return Response({'error': 'Invalid token.'})

        if recovery_instance.expires_at < timezone.now():
            return Response({'error': 'Token has expired.'})

        user = recovery_instance.user
        user.set_password(new_password)
        user.save()
        recovery_instance.delete()
        return Response({'detail': 'Password has been reset.'})

class LoginView(ObtainAuthToken):
    permission_classes = (AllowAny,)  

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    
class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)  

    def get(self, request):

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)