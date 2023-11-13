"""Views for user API"""
from rest_framework import generics, authentication, permissions, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from user.serializers import (
    UserSerializer,
    AuthtokenSerializer,
    ActiveAccountSerializer,
    ChangeActiveAccountSerializer,
    AccountSerializer,

)
from core.models import ActiveAccount, Account


class CreateUserView(generics.CreateAPIView):
    """View for create user"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create auth token view."""
    serializer_class = AuthtokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ActiveAccountView(
        generics.RetrieveUpdateAPIView,
        ):
    """Manage authenticated user."""
    serializer_class = ActiveAccountSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActiveAccount.objects.filter(user=self.request.user)

    def get_object(self):
        return self.get_queryset().first()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ChangeActiveAccountSerializer
        return self.serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @extend_schema(request=ChangeActiveAccountSerializer, methods=['PUT', 'PATCH'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(request=ChangeActiveAccountSerializer, methods=['PUT', 'PATCH'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class AccountListView(generics.ListAPIView, generics.CreateAPIView):
    """List all accounts for a user."""
    serializer_class = AccountSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

