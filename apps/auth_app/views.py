from rest_framework import generics, permissions, response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import MeSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        return response.Response(
            {"detail": "Password reset flow should be connected to email provider."}
        )


LoginView = TokenObtainPairView
RefreshView = TokenRefreshView
