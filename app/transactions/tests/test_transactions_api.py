"""Test for transactions APIS"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Transaction, ActiveAccount
from user.serializers import AccountSerializer
from django.contrib.auth import get_user_model

TRANSACTION_URL = reverse('transactions:transaction-list')

User = get_user_model()

class TransactionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234', email='ychag@example.com')
        self.client.force_authenticate(self.user)
        self.account = ActiveAccount.objects.get(user=self.user).account

    def test_list_transactions(self):
        """Test list of transactions"""
        Transaction.objects.create(
            account=self.account,
            amount=100,
            date='2020-01-01',
            description='test',
            transaction_type=Transaction.INCOME
            )
        Transaction.objects.create(
            account=self.account,
            amount=200,
            date='2020-01-02',
            description='test2',
            transaction_type=Transaction.EXPENSE
            )

        response = self.client.get(TRANSACTION_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

