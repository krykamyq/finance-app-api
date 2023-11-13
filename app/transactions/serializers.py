from rest_framework import serializers
from core.models import Transaction

"""Serializers for transactions"""
from user.serializers import AccountSerializer
from core.models import Transaction, Account, Category, Budget

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']

class TransactionSerializer(serializers.ModelSerializer):
    account = AccountSerializer(many=False)
    category = CategorySerializer(many=False, required=False)
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'date', 'description', 'transaction_type', 'category']
        read_only_fields = ['id']

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'date', 'description']
        read_only_fields = ['id']


class ExpenseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, required=False)
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'date', 'description', 'category']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        # Extract category data from validated_data
        category_data = validated_data.pop('category', None)

        # Create or retrieve the category instance
        if category_data:
            category, _ = Category.objects.get_or_create(user=user, **category_data)
            validated_data['category'] = category

        # Create the Expense instance
        expense = Transaction.objects.create(**validated_data)

        return expense

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

class BudgetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, required=False)
    class Meta:
        model = Budget
        fields = ['id', 'category', 'amount', 'spent']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        # Extract category data from validated_data
        category_data = validated_data.pop('category', None)

        # Create or retrieve the category instance
        if category_data:
            category, _ = Category.objects.get_or_create(user=user, **category_data)
            validated_data['category'] = category

        # Create the Expense instance
        budget = Budget.objects.create(**validated_data)

        return budget
