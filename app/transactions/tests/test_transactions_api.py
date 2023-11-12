"""Test for transactions APIS"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Transaction, ActiveAccount
from user.serializers import AccountSerializer
from django.contrib.auth import get_user_model

TRANSACTION_URL = reverse('transactions:transaction-list')
INCOMES_URL = reverse('transactions:income-list')

def detail_url(id):
    return reverse('transactions:income-detail', args=[id])

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
            amount=300,
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

    def test_create_income_transaction(self):
        """Test creating an income transaction"""
        payload = {
            'amount': '100.00',
            'date': '2020-01-01',
            'description': 'test',
        }
        response = self.client.post(INCOMES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], payload['amount'])
        self.assertEqual(response.data['date'], payload['date'])
        self.assertEqual(response.data['description'], payload['description'])

        income = Transaction.objects.get(
            account=self.account,
            amount=payload['amount'],
            date=payload['date'],
            description=payload['description'],)
        self.assertEqual(income.transaction_type, Transaction.INCOME)

    def test_list_income_transactions(self):
        """Test list of income transactions"""
        Transaction.objects.create(
            account=self.account,
            amount=300,
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

        response = self.client.get(INCOMES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_income_transactions(self):
        """Test updating an income transaction"""
        transaction = Transaction.objects.create(
            account=self.account,
            amount=300,
            date='2020-01-01',
            description='test',
            transaction_type=Transaction.INCOME
            )
        payload = {
            'amount': '100.00',
            'date': '2020-01-01',
            'description': 'test',
        }
        url = detail_url(transaction.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], payload['amount'])
        self.assertEqual(response.data['date'], payload['date'])
        self.assertEqual(response.data['description'], payload['description'])

    def test_delete_income_transactions(self):
        """Test deleting an income transaction"""
        transaction = Transaction.objects.create(
            account=self.account,
            amount=300,
            date='2020-01-01',
            description='test',
            transaction_type=Transaction.INCOME
            )
        url = detail_url(transaction.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.account.refresh_from_db()
        self.assertEqual(Transaction.objects.all().count(), 0)
        self.assertEqual(self.account.balance, 0)

