"""Urls for user API"""
from django.urls import path

from user.views import (
    CreateTokenView,
    CreateUserView,
    ManageUserView,
    ActiveAccountView,
)

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('active/', ActiveAccountView.as_view(), name='active'),
    ]