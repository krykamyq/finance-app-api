"""API for transactions handelling"""

from rest_framework import generics, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Transaction, ActiveAccount, Account
from transactions.serializers import TransactionSerializer, IncomeSerializer, ExpenseSerializer, TransferSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema


class TransactionList(generics.ListAPIView):
    """List transactions"""
    serializer_class = TransactionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        """Return objects for te user"""
        user_accounts = Account.objects.filter(user=self.request.user)
        return Transaction.objects.filter(account__in=user_accounts)

class baseViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for te current active account"""
        return Transaction.objects.filter(
            account=ActiveAccount.objects.get(
                user=self.request.user).account,
            transaction_type=self.transaction_type)

    def perform_create(self, serializer):
        """Create and save a new Income"""
        serializer.save(account=ActiveAccount.objects.get(
            user=self.request.user).account,
                        transaction_type=self.transaction_type)


class IncomeViewSet(baseViewSet):
    """Handle creating and updating Income objects"""
    serializer_class = IncomeSerializer
    transaction_type = 'income'


class ExpenseViewSet(baseViewSet):
    """Handle creating and updating Expense objects"""
    serializer_class = ExpenseSerializer
    transaction_type = 'expense'

class TransferAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = TransferSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            data = serializer.validated_data
            Transaction.create_transfer(
                data['from_account'],
                data['to_account'],
                data['amount'],
                data['description']
            )
            return Response({'status': 'transfer successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)