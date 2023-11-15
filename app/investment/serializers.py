from rest_framework import serializers

from core.models import Asset
from investment.load_data import fetch_and_update_stock_data

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['id']



