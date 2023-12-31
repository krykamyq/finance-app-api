from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
import logging
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


#########################################################################
#USER MODEL
#########################################################################


class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, username, password=None, **extra_fields):
        """Create, save and return new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
            )
        user.set_password(password)
        user.save(using=self._db)
        account = Account.objects.create(user=user, name='Base')
        ActiveAccount.objects.create(user=user, account=account)
        investment_account = InvestmentAccount.objects.create(user=user, name='Investment Account')
        ActiveInvestmentAccount.objects.create(user=user, investment_account=investment_account)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        """Create,save and return new superuser."""
        user = self.create_user(email, username, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.username

################################################################
#ACCOUNT AND TRANSACTION MODEL
################################################################

class Category(models.Model):
    """Category model"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Account(models.Model):
    """Account model"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s account: {self.name}"

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)  # Save the account instance first

        # Recalculate and update the user's total balance
        total_balance = sum(account.balance for account in Account.objects.filter(user=self.user))
        self.user.balance = total_balance
        self.user.save()

    def delete(self, *args, **kwargs):
        if ActiveAccount.objects.get(user=self.user).account == self:
            raise ValidationError("You cannot delete the active account")
        super(Account, self).delete(*args, **kwargs)  # Delete the account instance first

        # Recalculate and update the user's total balance
        total_balance = sum(account.balance for account in Account.objects.filter(user=self.user))
        self.user.balance = total_balance
        self.user.save()

class ActiveAccount(models.Model):
    """Active account model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='active_account'
    )
    account = models.OneToOneField(
        'Account',  # Assuming 'Account' is your account model
        on_delete=models.CASCADE,
        related_name='active_for_user'
    )

    def __str__(self):
        return f"{self.user.username}'s active account: {self.account.name}"


class Transaction(models.Model):
    """Transaction model"""
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.account.name} - {self.amount} - {self.transaction_type}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk and not self._state.adding:
                old_transaction = self.__class__.objects.get(pk=self.pk)
                old_amount = old_transaction.amount
            else:
                old_amount = 0  # For a new transaction, the old amount is 0


            balance_adjustment = self.amount - old_amount

            if self.transaction_type == self.EXPENSE:
                # Calculate the potential new balance
                new_balance = self.account.balance - balance_adjustment

                if new_balance < 0:
                    raise ValidationError("Expense amount cannot exceed account balance.")
                self.account.balance = new_balance

                # Update corresponding budget's spent amount
                self._update_budget_spent(balance_adjustment)

            elif self.transaction_type == self.INCOME:
                # Adjust the balance for the income, considering any previous amount if updating
                self.account.balance += balance_adjustment
                self._update_budget_spent(balance_adjustment)

            self.account.save()

            super(Transaction, self).save(*args, **kwargs)

    def _update_budget_spent(self, amount):
        """
        Update the spent amount in the budget corresponding to this transaction's category.
        Only update if the transaction type is EXPENSE.
        """
        if self.category and self.transaction_type == self.EXPENSE:
            budget, created = Budget.objects.get_or_create(
                user=self.account.user,
                category=self.category,
                defaults={'amount': amount, 'spent': amount}
            )
            if not created:
                budget.spent = budget.spent + amount
                if budget.spent > budget.amount:
                    raise ValidationError("Budget spent amount cannot exceed budget amount.")
                budget.save()



    def delete(self, *args, **kwargs):
        with transaction.atomic():
            # Adjust the account balance before deletion
            balance_adjustment = -self.amount if self.transaction_type == self.INCOME else self.amount
            self.account.balance += balance_adjustment

            # Optionally, validate negative balance
            if self.account.balance < 0:
                raise ValidationError("Deleting this transaction would result in a negative account balance.")

            # Update the corresponding budget's spent amount if it's an expense
            if self.transaction_type == self.EXPENSE and self.category:
                self._update_budget_spent(-self.amount)

            self.account.save()
            super(Transaction, self).delete(*args, **kwargs)

    @staticmethod
    def create_transfer(from_account, to_account, amount, description):
        if from_account.balance < amount:
            raise ValidationError("Insufficient funds in the source account.")

        with transaction.atomic():
            # Create Expense in source account
            Transaction.objects.create(
                account=from_account,
                amount=amount,
                transaction_type=Transaction.EXPENSE,
                date=timezone.now(),
                description=description
            )
            from_account.save()

            # Create Income in destination account
            Transaction.objects.create(
                account=to_account,
                amount=amount,
                transaction_type=Transaction.INCOME,
                date=timezone.now(),
                description=description
            )
            to_account.save()

    @staticmethod
    def transfer_to_investment_account(from_account, to_account, amount):
        if from_account.balance < amount:
            raise ValidationError("Insufficient funds in the source account.")

        with transaction.atomic():
            # Create Income in source account
            Transaction.objects.create(
                account=from_account,
                amount=amount,
                transaction_type=Transaction.EXPENSE,
                date=timezone.now(),
                description="Transfer to investment account"
            )
            from_account.save()

            to_acc = InvestmentAccount.objects.get(id=to_account.id)
            to_acc.amount_to_invest +=amount
            to_acc.save()



class Budget(models.Model):
    """Budget model"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)



    def __str__(self):
        return f"{self.user.username}'s budget on{self.category.name}: {self.amount}"


########################################################################
#INVESTIMENT ACCOUNT AND INVESTMENT TRANSACTION MODEL
########################################################################


class InvestmentAccount(Account):
    """Investment account model"""
    amount_to_invest = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_investment = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def actual_balance(self):
        return self.amount_to_invest + self.total_investment

    def total_investments(self):
        return InvestmentAsset.objects.filter(
            investment_account=self
        ).aggregate(
            total=Sum('total_value')
        )['total'] or Decimal('0.00')

    def save(self, *args, **kwargs):
        # If there are multiple operations that need to be atomic, use transaction.atomic()
        with transaction.atomic():
            self.total_investment = self.total_investments()
            self.balance = self.actual_balance()
            super(InvestmentAccount, self).save(*args, **kwargs)

            total_balance = sum(account.balance for account in Account.objects.filter(user=self.user))
            self.user.balance = total_balance
            self.user.save()# Save changes to the database

    def delete(self, *args, **kwargs):
        with transaction.atomic():

            invest = InvestmentAsset.objects.filter(investment_account=self)
            if invest:
                for i in invest:
                    i.delete()
            active = ActiveAccount.objects.get(user = self.user).account
            active.balance = self.actual_balance()
            super(InvestmentAccount, self).delete(*args, **kwargs)
            active.save()

    def __str__(self):
        return f"{self.user.username}'s investment account: {self.name}"


class ActiveInvestmentAccount(models.Model):
    """Active investment account model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='active_investment_account'
    )
    investment_account = models.OneToOneField(
        InvestmentAccount,
        on_delete=models.CASCADE,
        related_name='active_investment_for_user'
    )

    def __str__(self):
        return f"{self.user.username}'s active investment account: {self.investment_account.name}"


class Asset(models.Model):
    """Asset model"""
    name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=10, decimal_places=4)
    updated_at = models.DateTimeField(auto_now=True)
    type_asset = models.CharField(max_length=255, default="Stock")

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Sprawdzam, czy Asset jest używany w InvestmentAsset
        if InvestmentAsset.objects.filter(asset=self).exists():
            raise ValidationError("Nie można usunąć Asset, ponieważ jest używany w InvestmentAsset.")

        # Jeśli Asset nie jest używany, kontynuuj z usuwaniem
        super(Asset, self).delete(*args, **kwargs)


class InvestmentAsset(models.Model):
    """Investment asset model"""
    investment_account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity_have = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def total_values(self):
        self.total_value = self.quantity_have * self.asset.value


    def save(self, *args, **kwargs):
        # If there are multiple operations that need to be atomic, use transaction.atomic()
        with transaction.atomic():
            self.total_values()
            super(InvestmentAsset, self).save(*args, **kwargs)  # Save changes to the database

    def delete(self, *args, **kwargs):
        if self.quantity_have > 0:
            raise ValidationError("Nie można usunąć InvestmentAsset, poniewaz quantity jest wieksza od 0")
        else:
            super(InvestmentAsset, self).delete(*args, **kwargs)


class InvestmentTransaction(models.Model):
    """Investment transaction model"""
    investment_account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE)
    asset = models.ForeignKey(InvestmentAsset, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    initial_value = models.DecimalField(max_digits=10, decimal_places=4)
    description = models.CharField(max_length=255, blank=True)
    class type_transactions(models.TextChoices):
        BUY = 'buy', 'Buy'
        SELL ='sell', 'Sell'
    type_transaction = models.CharField(max_length=255, choices=type_transactions.choices, default=type_transactions.BUY)


    def save(self, *args, **kwargs):
        # Check if this is a new transaction or an update
        is_new = self._state.adding
        old_quantity = None

        # If updating, get the old transaction quantity
        if not is_new:
            old_transaction = InvestmentTransaction.objects.get(pk=self.pk)
            old_quantity = old_transaction.quantity

        with transaction.atomic():
            # Update the asset quantity
            if is_new:
                self._update_asset_quantity_new_transaction()
            else:
                self._update_asset_quantity_existing_transaction(old_quantity)

            # Save the transaction
            super(InvestmentTransaction, self).save(*args, **kwargs)

    def _update_asset_quantity_new_transaction(self):
        if self.type_transaction == self.type_transactions.BUY:
            if self.investment_account.amount_to_invest < self.quantity * self.initial_value:
                raise ValidationError("Cannot buy more assets than you have fund in the account.")
            self.asset.quantity_have += self.quantity
            self.investment_account.amount_to_invest -= self.quantity * self.initial_value
        elif self.type_transaction == self.type_transactions.SELL:
            if self.quantity > self.asset.quantity_have:
                raise ValidationError("Cannot sell more assets than are held in the account.")
            self.asset.quantity_have -= self.quantity
            self.investment_account.amount_to_invest += self.quantity * self.initial_value
        self.asset.save()
        self.investment_account.save()

    def _update_asset_quantity_existing_transaction(self, old_quantity):
        quantity_diff = self.quantity - old_quantity
        if quantity_diff != 0:
            if self.type_transaction == self.type_transactions.BUY:
                if self.investment_account.amount_to_invest < quantity_diff * self.initial_value:
                    raise ValidationError("Cannot buy more assets than you have fund in the account.")
                self.asset.quantity_have += quantity_diff
                self.investment_account.amount_to_invest -= quantity_diff * self.initial_value
            elif self.type_transaction == self.type_transactions.SELL:
                new_quantity_have = self.asset.quantity_have - quantity_diff
                if new_quantity_have < 0:
                    raise ValidationError("Cannot sell more assets than are held in the account.")
                self.asset.quantity_have = new_quantity_have
                self.investment_account.amount_to_invest += quantity_diff * self.initial_value
        self.asset.save()
        self.investment_account.save()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.type_transaction is self.type_transactions.BUY:
                if self.asset.quantity_have < self.quantity:
                    raise ValidationError("Cannot delete transactions if you don't have enougt quantity in the account.")
                self.asset.quantity_have -= self.quantity
                self.investment_account.amount_to_invest += self.quantity * self.initial_value
            else:
                if self.investment_account.amount_to_invest < self.quantity * self.initial_value:
                    raise ValidationError("Cannot delete transactions if you don't have enougt ammount to invest in the account.")
                self.asset.quantity_have += self.quantity
                self.investment_account.amount_to_invest -= self.quantity * self.initial_value
            super(InvestmentTransaction, self).delete(*args, **kwargs)
            self.asset.save()
            self.investment_account.save()
