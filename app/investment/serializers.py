from rest_framework import serializers

from core.models import Asset, InvestmentAccount, InvestmentAsset, InvestmentTransaction, ActiveInvestmentAccount


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['id']


class InvestmentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentAccount
        fields = ['id', 'name', 'balance', 'amount_to_invest', 'total_investment']
        read_only_fields = ['id', 'balance', 'total_investment']


class InvestmentAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentAsset
        fields = ['id', 'investment_account', 'asset', 'quantity_have', 'total_value']
        read_only_fields = ['id', 'total_value']


class InvestmentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentTransaction
        fields = ['id', 'investment_account', 'asset', 'quantity', 'date', 'initial_value', 'description', 'type_transaction']
        read_only_fields = ['id']

class BuyAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentTransaction
        fields = ['id', 'investment_account', 'asset', 'quantity', 'date', 'initial_value', 'description']
        read_only_fields = ['id']

class SellAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentTransaction
        fields = ['id', 'investment_account', 'asset', 'quantity', 'date', 'initial_value', 'description']
        read_only_fields = ['id']

class ActiveInvestmentAccountSerializer(serializers.ModelSerializer):
    investment_account  = InvestmentAccountSerializer()
    class Meta:
        model = ActiveInvestmentAccount
        fields = ['investment_account']


class ChangeActiveInvestmentAccountSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()

    def validate_account_id(self, value):
        user = self.context['request'].user
        if not InvestmentAccount.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Account not found or does not belong to the user.")
        return value

    def update(self, instance, validated_data):
        account_id = validated_data.get('account_id')
        new_account = InvestmentAccount.objects.get(id=account_id)
        instance.investment_account = new_account
        instance.save()
        return instance






