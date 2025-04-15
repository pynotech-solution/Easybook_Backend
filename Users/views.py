from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics
from .serializers import UserSerializer, ProfileSerializer
from .models import User
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(TokenObtainPairView):
    """
    Custom Login View to handle user authentication using JWT.
    Inherits from TokenObtainPairView to provide access and refresh tokens.
    """
    pass

class RefreshTokenView(TokenRefreshView):
    """
    Custom Refresh Token View to handle token refreshing.
    Inherits from TokenRefreshView to provide a new access token.
    """
    pass

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


    def get_object(self):
        return self.request.user