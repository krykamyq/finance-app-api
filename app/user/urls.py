"""Urls for user API"""
from django.urls import path

from user.views import (
    CreateTokenView,
    CreateUserView,
    ManageUserView,
    ActiveAccountView,
    AccountListView,
)

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
    path('active-account/', ActiveAccountView.as_view(), name='active-account'),
    path('accounts/', AccountListView.as_view(), name='accounts'),
    ]