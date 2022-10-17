from django.db import models
from django.urls import reverse

from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.sites.models import Site

from datetime import datetime


class LoginExpire(models.Model):
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=100)
    expire_date = models.DateField()

    def __str__(self):
        return self.title


class Office(models.Model):
    name = models.CharField(max_length=30, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=11)
    address = models.TextField()
    status = models.BooleanField(default=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(_('email address'), blank=True, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateField(_('date joined'), default=timezone.now)

    def __str__(self):
        return self.username


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=254)
    is_active = models.BooleanField(default=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added', '-id']

    def __str__(self):
        return self.name

    def get_update_url(self):
        return reverse("supplier-update", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        return reverse("supplier-delete", kwargs={"pk": self.pk})
    

class PurchaseProduct(models.Model):
    supplier = models.ForeignKey(Supplier, blank=True, null=True, on_delete=models.SET_NULL)
    
    product_name = models.CharField(max_length=30, default='Wheat')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    chalan_number = models.CharField(max_length=30, blank=True, null=True)

    date_added = models.DateField(default=datetime.today)
    date_updated = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_added', '-id']

    def __str__(self):
        return self.product_name

    def get_update_url(self):
        return reverse("purchase-update", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        return reverse("purchase-delete", kwargs={"pk": self.pk})

    @property
    def total_purchase_price(self):
        return (self.quantity * self.price)


class Stock(models.Model):
    product_name = models.CharField(max_length=30)
    quantity = models.PositiveIntegerField()
    # sell_price = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)

    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_updated', '-id']

    def __str__(self):
        return self.product_name

    def get_update_url(self):
        return reverse("stock-update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse("stock-delete", kwargs={"pk": self.pk})


class SellProduct(models.Model):
    SACK_CHOICES = (
        (5, '5 kg'),
        (35, '35 kg'),
        (37, '37 kg'),
        (50, '50 kg'),
        (55, '55 kg'),
        (60, '60 kg')
    )

    product_name = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL)
    product_label = models.CharField(max_length=254, blank=True, null=True)
    sack = models.IntegerField(choices=SACK_CHOICES)
    quantity = models.PositiveIntegerField()
    sell_price = models.DecimalField(max_digits=8, decimal_places=2)
    customer_name = models.CharField(max_length=30)
    token_number = models.CharField(max_length=11)
    paid_amount = models.DecimalField(max_digits=8, decimal_places=2)

    date_added = models.DateField(default=datetime.today)
    date_updated = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_added', '-id']

    def __str__(self):
        if self.product_name:
            return str(self.product_name)
        return self.product_label

    def save(self, *args, **kwargs):
        self.product_label = str(self.product_name)
        super(SellProduct, self).save(*args, **kwargs)

    def get_update_url(self):
        return reverse("sell-update", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        return reverse("sell-delete", kwargs={"pk": self.pk})

    @property
    def is_paid(self):
        if self.paid_amount == 0:
            return True
        else:
            return False

    @property
    def get_total_amount(self):
        return (self.sell_price * self.quantity)

    @property
    def get_due_amount(self):
        return (self.get_total_amount - self.paid_amount)
