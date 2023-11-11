"""Views for user API"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
)


class CreateUserViwe(generics.CreateAPIView):
    """View for create user"""
    serializer_class = UserSerializer

