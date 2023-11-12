"""API for transactions handelling"""

from rest_framework import generics, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Transaction, ActiveAccount
from transactions.serializers import TransactionSerializer, IncomeSerializer


class TransactionList(generics.ListAPIView):
    """List transactions"""
    serializer_class = TransactionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        """Return objects for te current active account"""
        return Transaction.objects.filter(account=ActiveAccount.objects.get(user=self.request.user).account)

class IncomeViewSet(viewsets.ModelViewSet):
    """Handle creating and updating Income objects"""
    serializer_class = IncomeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        """Return objects for te current active account"""
        return Transaction.objects.filter(
            account=ActiveAccount.objects.get(
                user=self.request.user).account,
            transaction_type='income')

    def perform_create(self, serializer):
        """Create and save a new Income"""
        serializer.save(account=ActiveAccount.objects.get(user=self.request.user).account, transaction_type='income')