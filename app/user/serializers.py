"""Serializers for user API"""
from django.contrib.auth import (
    get_user_model,

    )
from django.utils.translation import gettext as _
from rest_framework import serializers



class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password')
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
               'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """Create and return a new user"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return an existing user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
