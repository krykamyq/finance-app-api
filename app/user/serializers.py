"""Serializers for user API"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
    )
from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import ActiveAccount, Account


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'balance')
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


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for the account"""
    class Meta:
        model = Account
        fields = ('id', 'name', 'balance')
        read_only_fields = ['id']


class ActiveAccountSerializer(serializers.ModelSerializer):
    """Serializer for the active account"""
    account = AccountSerializer(many=False)
    class Meta:
        model = ActiveAccount
        fields = ['account']


class ChangeActiveAccountSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()

    def validate_account_id(self, value):
        user = self.context['request'].user
        if not Account.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Account not found or does not belong to the user.")
        return value

    def update(self, instance, validated_data):
        account_id = validated_data.get('account_id')
        new_account = Account.objects.get(id=account_id)
        instance.account = new_account
        instance.save()
        return instance


class AuthtokenSerializer(serializers.Serializer):
    """Serializer for the user token"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate user."""
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with proviided credentials.')
            raise serializers.ValidationError(msg, code='autorization')

        attrs['user'] = user

        return attrs
