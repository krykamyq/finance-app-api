from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError


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

    def __str__(self):
        return f"{self.account.name} - {self.amount} - {self.transaction_type}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk and not self._state.adding:
                old_transaction = self.__class__.objects.get(pk=self.pk)
                old_amount = old_transaction.amount
            else:
                old_amount = 0  # For a new transaction, the old amount is 0


            if self.transaction_type == self.EXPENSE:
                # Calculate the potential new balance
                new_balance = self.account.balance + old_amount - self.amount

                if new_balance < 0:
                    raise ValidationError("Expense amount cannot exceed account balance.")
                self.account.balance = new_balance

            elif self.transaction_type == self.INCOME:
                # Adjust the balance for the income, considering any previous amount if updating
                self.account.balance = self.account.balance - old_amount + self.amount

            self.account.save()
            super(Transaction, self).save(*args, **kwargs)