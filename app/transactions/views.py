"""API for transactions handelling"""

from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Transaction, ActiveAccount
from transactions.serializers import TransactionSerializer


class TransactionList(generics.ListAPIView):
    """List transactions"""
    serializer_class = TransactionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        """Return objects for te current active account"""
        return Transaction.objects.filter(account=ActiveAccount.objects.get(user=self.request.user).account)
