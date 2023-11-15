from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, authentication
from investment.serializers import AssetSerializer
from core.models import Asset
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from investment.load_data import fetch_and_update_stock_data


class AssetList(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny]


class UpdateStockDataView(APIView):
    """
    API endpoint that triggers fetching and updating stock data.
    """
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication]

    def get(self, request, format=None):
        try:
            fetch_and_update_stock_data()
            return Response({'status': 'Stock data updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
