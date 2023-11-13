"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Account, ActiveAccount, Transaction
from decimal import Decimal



def create_user(email="test@example.com",
                username='test123',
                password="test123"
                ):
    return get_user_model().objects.create_user(email, username, password)


class MotelTest(TestCase):
    """Test models."""
    def test_create_user_with_email_successful(self):
        """Test createing user with email is successful"""

        email = 'test@example.com'
        username = 'test123'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@example.com', 'test1@example.com', 'test1'],
            ['TEST2@example.com', 'TEST2@example.com', 'test2'],
            ['Test3@example.com', 'Test3@example.com', 'test3'],
            ['test4@EXAMPLE.com', 'test4@example.com', 'test4'],
            ['test5@example.COM', 'test5@example.com', 'test5'],
        ]

        for email, expected, username in sample_emails:
            user = create_user(email=email, username=username,
                               password='password123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            create_user(email=None, username='test123', password='password123')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_account_for_user(self):
        """Test creating an account for a user"""
        user = get_user_model().objects.create_user(
            'test@user.com',
            'testuser',
            'test123'
        )
        account = Account.objects.create(user=user, name='Savings')

        self.assertEqual(account.user, user)
        self.assertEqual(account.name, 'Savings')
        self.assertEqual(account.balance, 0)

    def test_create_active_account_for_user(self):
        """Test creating an active account for a user"""
        user = get_user_model().objects.create_user(
            'test@user.com',
            'testuser',
            'test123'
        )
        active = ActiveAccount.objects.get(user=user)
        account = Account.objects.get(pk=active.account.id)

        self.assertEqual(active.user, user)
        self.assertEqual(active.account, account)

    def test_create_transaction(self):
        """Test creating a transaction is successful"""
        user = create_user()
        active = ActiveAccount.objects.get(user=user).account
        transaction = Transaction.objects.create(
            account=active,
            amount=100,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.INCOME
        )

        self.assertEqual(transaction.account, active)
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.description, 'Test Transaction')
        self.assertEqual(transaction.transaction_type, Transaction.INCOME)

    def test_successful_transfer(self):
        """Test a successful transfer between accounts"""
        user = create_user()
        self.account1 = Account.objects.create(user=user, balance=1000)
        self.account2 = Account.objects.create(user=user, balance=500)
        Transaction.create_transfer(self.account1, self.account2, 400, 'Test Transfer')

        self.account1.refresh_from_db()
        self.account2.refresh_from_db()

        self.assertEqual(self.account1.balance, Decimal('600'))
        self.assertEqual(self.account2.balance, Decimal('900'))

    def test_transfer_with_insufficient_funds(self):
        """Test transfer with insufficient funds raises an error"""
        user = create_user()
        self.account1 = Account.objects.create(user=user, balance=1000)
        self.account2 = Account.objects.create(user=user, balance=500)

        with self.assertRaises(ValueError):
            Transaction.create_transfer(self.account1, self.account2, 1500, 'Failed Transfer')

        # Optionally, verify that balances remain unchanged
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, 1000)
        self.assertEqual(self.account2.balance, 500)




