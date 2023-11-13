from rest_framework import serializers
from core.models import Transaction

"""Serializers for transactions"""
from user.serializers import AccountSerializer
from core.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    account = AccountSerializer(many=False)
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'date', 'description', 'transaction_type']
        read_only_fields = ['id']

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'date', 'description']
        read_only_fields = ['id']


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'date', 'description']
        read_only_fields = ['id']