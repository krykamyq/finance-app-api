"""Test for transactions APIS"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Transaction, ActiveAccount, Account, Budget, Category
from user.serializers import AccountSerializer
from django.contrib.auth import get_user_model

TRANSACTION_URL = reverse('transactions:transaction-list')
INCOMES_URL = reverse('transactions:income-list')
EXPENSES_URL = reverse('transactions:expense-list')
TRANSFER_URL = reverse('transactions:transfer')
BUDGETS_URL = reverse('transactions:budget-list')

def detail_url(id):
    return reverse('transactions:income-detail', args=[id])
def detail_url2(id):
    return reverse('transactions:expense-detail', args=[id])
def detail_url3(id):
    return reverse('transactions:budget-detail', args=[id])

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

    def test_create_expense_transactions(self):
        """test creating an expense transaction"""
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
        response = self.client.post(EXPENSES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], payload['amount'])
        self.assertEqual(response.data['date'], payload['date'])
        self.assertEqual(response.data['description'], payload['description'])

        expense = Transaction.objects.get(
            account=self.account,
            amount=payload['amount'],
            date=payload['date'],
            description=payload['description'],)
        self.assertEqual(expense.transaction_type, Transaction.EXPENSE)


    def test_list_expense_transactions(self):
        """Test list of expense transactions"""
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

        response = self.client.get(EXPENSES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_update_expense_transactions(self):
        """Test updating an expense transaction"""
        transaction = Transaction.objects.create(
            account=self.account,
            amount=300,
            date='2020-01-01',
            description='test',
            transaction_type=Transaction.INCOME
            )
        transaction2 = Transaction.objects.create(
            account=self.account,
            amount=100,
            date='2020-01-01',
            description='test',
            transaction_type=Transaction.EXPENSE
            )
        payload = {
            'amount': '100.00',
            'date': '2020-01-01',
            'description': 'test',
        }
        url = detail_url2(transaction2.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], payload['amount'])
        self.assertEqual(response.data['date'], payload['date'])
        self.assertEqual(response.data['description'], payload['description'])


    def test_delete_expense_transactions(self):
        """Test deleting an expense transaction"""
        transaction = Transaction.objects.create(
            account=self.account,
            amount=300,
            date='2020-01-01',
            description='test',
            transaction_type=Transaction.INCOME
            )
        transaction2 = Transaction.objects.create(
            account=self.account,
            amount=100,
            date='2020-01-01',
            description='test',
            transaction_type=Transaction.EXPENSE
            )
        url = detail_url2(transaction2.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.account.refresh_from_db()
        self.assertEqual(Transaction.objects.all().count(), 1)
        self.assertEqual(self.account.balance, 300)

    def test_transfer_success(self):
        """Test successful transfer between accounts"""
        from_account = Account.objects.create(user=self.user, name='Savings', balance=1000)
        to_account = Account.objects.create(user=self.user, name='Current', balance=1000)
        payload = {
            'from_account_id': from_account.id,
            'to_account_id': to_account.id,
            'amount': '200.00',
            'description': 'Test Transfer'
        }
        response = self.client.post(TRANSFER_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'transfer successful')

        from_account.refresh_from_db()
        to_account.refresh_from_db()

        self.assertEqual(from_account.balance, 800)
        self.assertEqual(to_account.balance, 1200)


    def test_add_expense_with_category(self):
        """test creating an expense transaction"""
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
            'category': {'name': 'test',}
        }
        response = self.client.post(EXPENSES_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], payload['amount'])
        self.assertEqual(response.data['date'], payload['date'])
        self.assertEqual(response.data['description'], payload['description'])
        self.assertTrue(Budget.objects.filter(user=self.user, category=Category.objects.get(name='test', user=self.user)).exists())

        expense = Transaction.objects.get(
            account=self.account,
            amount=payload['amount'],
            date=payload['date'],
            description=payload['description'],)
        self.assertEqual(expense.transaction_type, Transaction.EXPENSE)

    def test_create_budget(self):
        """test creating a budget"""
        payload = {
            'amount': '100.00',
            'category': {'name': 'test',}
        }
        response = self.client.post(BUDGETS_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], payload['amount'])
        self.assertTrue(Budget.objects.filter(user=self.user, category=Category.objects.get(name='test', user=self.user)).exists())

    def test_list_budgets(self):
        """Test list of budgets"""
        Budget.objects.create(user=self.user, amount=100, category=Category.objects.create(name='test', user=self.user))
        Budget.objects.create(user=self.user, amount=200, category=Category.objects.create(name='test2', user=self.user))

        response = self.client.get(BUDGETS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_budget(self):
        """Test updating a budget"""
        budget = Budget.objects.create(user=self.user, amount=100, category=Category.objects.create(name='test', user=self.user))
        payload = {
            'amount': '200.00'
        }
        url = detail_url3(budget.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], payload['amount'])

    def test_delete_budget(self):
        """Test deleting a budget"""
        budget = Budget.objects.create(user=self.user, amount=100, category=Category.objects.create(name='test', user=self.user))
        url = detail_url3(budget.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Budget.objects.all().count(), 0)
