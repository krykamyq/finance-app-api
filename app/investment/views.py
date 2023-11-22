from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, authentication, viewsets
from investment.serializers import AssetSerializer, InvestmentAccountSerializer, ActiveInvestmentAccountSerializer, ChangeActiveInvestmentAccountSerializer
from core.models import Asset, InvestmentAccount, ActiveInvestmentAccount
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from investment.load_data import fetch_and_update_stock_data
from drf_spectacular.utils import extend_schema


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

class AccountViewsets(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = InvestmentAccountSerializer

    def get_queryset(self):
        return InvestmentAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ActiveInvestmentAccountView(generics.RetrieveUpdateAPIView):
        """Manage authenticated user."""
        serializer_class = ActiveInvestmentAccountSerializer
        authentication_classes = [authentication.TokenAuthentication]
        permission_classes = [permissions.IsAuthenticated]

        def get_queryset(self):
            return ActiveInvestmentAccount.objects.filter(user=self.request.user)

        def get_object(self):
            return self.get_queryset().first()

        def get_serializer_class(self):
            if self.request.method in ['PUT', 'PATCH']:
                return ChangeActiveInvestmentAccountSerializer
            return self.serializer_class

        def get_serializer_context(self):
            context = super().get_serializer_context()
            context.update({"request": self.request})
            return context

        @extend_schema(request=ChangeActiveInvestmentAccountSerializer, methods=['PUT', 'PATCH'])
        def put(self, request, *args, **kwargs):
            return super().put(request, *args, **kwargs)

        @extend_schema(request=ChangeActiveInvestmentAccountSerializer, methods=['PUT', 'PATCH'])
        def patch(self, request, *args, **kwargs):
            return super().patch(request, *args, **kwargs)


