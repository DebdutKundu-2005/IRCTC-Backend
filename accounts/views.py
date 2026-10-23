from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer, MeSerializer



# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'phone': request.user.phone,
        })

@extend_schema(
    tags=['Authentication'],
    summary='Login',
    description='Login with username and password and receive JWT access and refresh tokens.',
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    tags=['Authentication'],
    summary='Refresh access token',
    description='Generate a new access token using a valid refresh token.',
)
class CustomTokenRefreshView(TokenRefreshView):
    pass
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MeSerializer,
        tags=['Authentication'],
        summary='Get current user',
        description='Returns the profile information of the currently authenticated user.',
    )
    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'phone': request.user.phone,
        })