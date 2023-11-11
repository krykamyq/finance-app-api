"""Urls for user API"""
from django.urls import path

from user.views import (CreateUserViwe
)

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserViwe.as_view(), name='create'),
]