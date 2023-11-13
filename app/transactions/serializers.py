from rest_framework import serializers
from core.models import Transaction

"""Serializers for transactions"""
from user.serializers import AccountSerializer
from core.models import Transaction, Account

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

class TransferSerializer(serializers.Serializer):
    from_account_id = serializers.IntegerField(write_only=True)
    to_account_id = serializers.IntegerField(write_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(max_length=255, required=False, default='Account Transfer')

    def validate(self, data):
        """
        Check that the accounts exist and belong to the user, and the source account has enough balance.
        """
        user = self.context['request'].user
        try:
            data['from_account'] = Account.objects.get(id=data['from_account_id'], user=user)
            data['to_account'] = Account.objects.get(id=data['to_account_id'], user=user)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Invalid account ID.")

        if data['from_account'].balance < data['amount']:
            raise serializers.ValidationError("Insufficient funds in the source account.")

        return data
