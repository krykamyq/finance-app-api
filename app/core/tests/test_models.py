"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Account, ActiveAccount, Transaction, Category, Budget, InvestmentAccount, ActiveInvestmentAccount
from decimal import Decimal
from django.core.exceptions import ValidationError



def create_user(email="test@example.com",
                username='test123',
                password="test123"
                ):
    return get_user_model().objects.create_user(email, username, password)


class ModelUserTest(TestCase):
    """Test models."""
    def test_create_user_with_email_successful(self):
        """Test createing user with email is successful"""

        email = 'test@example.com'
        username = 'test123'
        password = 'password123'
        users = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password
        )

        self.assertEqual(users.email, email)
        self.assertTrue(users.check_password(password))

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


class ModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user',
            password='test_password',
            email='test_email@test.com')
        self.account = ActiveAccount.objects.get(
            user=self.user).account


    def test_create_account_for_user(self):
        self.assertEquals(self.account.user, self.user)
        self.assertEquals(self.account.balance, 0)
        self.assertEquals(self.user.balance, 0)


    def test_create_income_transaction(self):
        """Test creating a transaction is successful"""
        transaction = Transaction.objects.create(
            account=self.account,
            amount=100,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.INCOME
        )

        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.description, 'Test Transaction')
        self.assertEqual(transaction.transaction_type, Transaction.INCOME)
        self.assertEqual(transaction.date, '2021-01-01')
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 100)

    def test_create_expense_transaction(self):
        """Test creating a transaction is successful"""
        Transaction.objects.create(
            account=self.account,
            amount=100,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.INCOME
        )
        transaction = Transaction.objects.create(
            account=self.account,
            amount=50,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.EXPENSE
        )

        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.amount, 50)
        self.assertEqual(transaction.description, 'Test Transaction')
        self.assertEqual(transaction.transaction_type, Transaction.EXPENSE)
        self.assertEqual(transaction.date, '2021-01-01')
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 50)

    def test_create_expense_with_not_enough_funds_raises_error(self):
        with self.assertRaises(ValidationError):
            transaction = Transaction.objects.create(
                account=self.account,
                amount=50,
                date='2021-01-01',
                description='Test Transaction',
                transaction_type=Transaction.EXPENSE
        )
    def test_delete_income_transaction(self):
        transaction = Transaction.objects.create(
            account=self.account,
            amount=100,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.INCOME
        )
        transaction.delete()
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 0)
        self.assertEqual(self.account.balance, 0)

    def test_delete_expense_transaction(self):
        Transaction.objects.create(
            account=self.account,
            amount=100,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.INCOME
        )
        transaction = Transaction.objects.create(
            account=self.account,
            amount=50,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.EXPENSE
        )
        transaction.delete()
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 100)
        self.assertEqual(self.account.balance, 100)

    def test_delete_account(self):
        acc = Account.objects.create(user= self.user, name='test')
        Transaction.objects.create(
            account=acc,
            amount=100,
            date='2021-01-01',
            description='Test Transaction',
            transaction_type=Transaction.INCOME
        )
        acc.delete()
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 0)

    def test_delete_active_account(self):
        with self.assertRaises(ValidationError):
            self.account.delete()

    def test_successful_transfer(self):
        """Test a successful transfer between accounts"""
        self.account2 = Account.objects.create(user=self.user, balance=500)
        Transaction.create_transfer(self.account2, self.account, 400, 'Test Transfer')

        self.account.refresh_from_db()
        self.account2.refresh_from_db()

        self.assertEqual(self.account.balance, Decimal('400'))
        self.assertEqual(self.account2.balance, Decimal('100'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal('500'))

    def test_transfer_with_insufficient_funds(self):
        """Test transfer with insufficient funds raises an error"""
        self.account2 = Account.objects.create(user=self.user, balance=500)

        with self.assertRaises(ValidationError):
            Transaction.create_transfer(self.account, self.account2, 1500, 'Failed Transfer')

        # Optionally, verify that balances remain unchanged
        self.account.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account.balance, 0)
        self.assertEqual(self.account2.balance, 500)

    def test_category_creation(self):
        """Test the category creation"""
        category = Category.objects.create(user=self.user, name='Groceries')
        self.assertEqual(category.name, 'Groceries')
        self.assertEqual(category.user, self.user)

    def test_delete_category(self):
        """Test the category deletion"""
        category = Category.objects.create(user=self.user, name='Groceries')
        category.delete()
        self.assertEqual(Category.objects.all().count(), 0)

    def test_budget_creation(self):
        """Test the budget creation"""
        category = Category.objects.create(user=self.user, name='Groceries')
        budget = Budget.objects.create(user=self.user, amount=1000, category=category)
        self.assertEqual(budget.user, self.user)
        self.assertEqual(budget.category, category)
        self.assertEqual(budget.amount, 1000)

    def test_transaction_creation_updates_budget(self):
        """Test creating an expense transaction updates the budget spent amount"""
        category = Category.objects.create(user=self.user, name='Groceries')
        budget = Budget.objects.create(user=self.user, amount=1000, category=category)
        Transaction.objects.create(
            account=ActiveAccount.objects.get(user=self.user).account,
            date='2021-01-01',
            amount=100,
            transaction_type=Transaction.INCOME)

        Transaction.objects.create(
            account=ActiveAccount.objects.get(user=self.user).account,
            category=budget.category,
            date='2021-01-01',
            amount=100,
            transaction_type=Transaction.EXPENSE,
        )

        budget.refresh_from_db()
        self.assertEqual(budget.spent, Decimal('100.00'))

    def test_transaction_creation_expense_is_to_hight_for_budget(self):
        category = Category.objects.create(user=self.user, name='Groceries')
        budget = Budget.objects.create(user=self.user, amount=10, category=category)
        Transaction.objects.create(
            account=ActiveAccount.objects.get(user=self.user).account,
            date='2021-01-01',
            amount=100,
            transaction_type=Transaction.INCOME)
        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                account=ActiveAccount.objects.get(user=self.user).account,
                category=budget.category,
                date='2021-01-01',
                amount=100,
                transaction_type=Transaction.EXPENSE,
            )

        budget.refresh_from_db()
        self.assertEqual(budget.spent, Decimal('0'))




    def test_transaction_creation_income_does_not_affect_budget(self):
        """Test creating an income transaction does not affect the budget"""
        user = create_user()
        category = Category.objects.create(user=user, name='Groceries')
        budget = Budget.objects.create(user=user, amount=1000, category=category)
        initial_spent = budget.spent
        Transaction.objects.create(
            account=ActiveAccount.objects.get(user=user).account,
            category=category,
            amount=100,
            date='2021-01-01',
            transaction_type=Transaction.INCOME
        )

        budget.refresh_from_db()
        self.assertEqual(budget.spent, initial_spent)

    def test_updating_transaction(self):
        """Test updating a transaction adjusts the budget correctly"""
        category = Category.objects.create(user=self.user, name='Groceries')
        budget = Budget.objects.create(user=self.user, amount=1000, category=category)
        Transaction.objects.create(
            account=self.account,
            date='2021-01-01',
            amount=200,
            transaction_type=Transaction.INCOME)
        transaction = Transaction.objects.create(
            account=self.account,
            category=category,
            date='2021-01-01',
            amount=100,
            transaction_type=Transaction.EXPENSE
        )
        transaction.amount = 150
        transaction.save()

        budget.refresh_from_db()
        self.assertEqual(budget.spent, 150)
        self.assertEqual(transaction.amount, 150)
        self.user.refresh_from_db()
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance,  Decimal('50'))
        self.assertEqual(self.user.balance, Decimal('50'))

    def test_deleting_transaction_reverts_budget(self):
        """Test deleting a transaction reverts the budget spent amount"""
        category = Category.objects.create(user=self.user, name='Groceries')
        budget = Budget.objects.create(user=self.user, amount=1000, category=category)
        Transaction.objects.create(
            account=self.account,
            date='2021-01-01',
            amount=200,
            transaction_type=Transaction.INCOME)
        transaction = Transaction.objects.create(
            account=self.account,
            category=category,
            date='2021-01-01',
            amount=100,
            transaction_type=Transaction.EXPENSE
        )
        transaction.delete()

        budget.refresh_from_db()
        self.assertEqual(budget.spent, 0)

    def test_transfer_to_investment_account(self):
        """Test a successful transfer between accounts"""
        Transaction.objects.create(
            account=self.account,
            date='2021-01-01',
            amount=200,
            transaction_type=Transaction.INCOME)
        account2 = ActiveInvestmentAccount.objects.get(user=self.user).investment_account
        Transaction.transfer_to_investment_account(self.account, account2, 100)

        self.account.refresh_from_db()
        account2.refresh_from_db()

        self.assertEqual(self.account.balance, Decimal('100'))
        self.assertEqual(account2.balance, Decimal('100'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal('200'))






