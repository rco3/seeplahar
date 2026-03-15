from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from .customer_context import get_current_customer

# /users/models.py


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, customer=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not customer:
            raise ValueError('The Customer field must be set')

        user = self.model(username=username, customer=customer, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Create or get a default customer for superusers
        default_customer, _ = Customer.objects.get_or_create(name="Superuser Customer")

        return self.create_user(username, password, customer=default_customer, **extra_fields)


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    photos = models.ManyToManyField('media.Photo', blank=True, related_name='customers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CustomerAwareQuerySet(QuerySet):
    def filter_by_current_customer(self):
        customer = get_current_customer()
        return self.filter(customer=customer) if customer else self.none()


class CustomerAwareManager(models.Manager):
    def get_queryset(self):
        queryset = CustomerAwareQuerySet(self.model, using=self._db)
        customer = get_current_customer()
        return queryset.filter(customer=customer) if customer else queryset

    def filter_by_current_customer(self):
        return CustomerAwareQuerySet(self.model, using=self._db).filter_by_current_customer()


class CustomerAwareModel(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    objects = CustomerAwareManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.customer_id:
            current_customer = get_current_customer()
            if not current_customer:
                raise ValidationError("No customer in context for CustomerAwareModel save")
            self.customer = current_customer
        super().save(*args, **kwargs)

# In users/models.py
class Partner(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    photos = models.ManyToManyField('media.Photo', blank=True, related_name='partners')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add other fields as needed

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ['customer', 'name']  # Ensures partner names are unique per customer


class User(AbstractUser, CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=30, unique=True, null=False, blank=False)
    photos = models.ManyToManyField('media.Photo', blank=True, related_name='users')
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    is_partner_admin = models.BooleanField(default=False)
    email = None  # This removes the email field

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def get_primary_email(self):
        primary_email = EmailAddress.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            is_primary=True
        ).first()
        return primary_email.email if primary_email else None


class ContactInfoType(CustomerAwareModel):
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ['customer', 'name']

    def __str__(self):
        return self.name


class ContactInfo(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    contact_function = models.ForeignKey(ContactInfoType, on_delete=models.PROTECT)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def clean(self):
        if not isinstance(self.content_object, (Customer, Partner, User)):
            raise ValidationError("ContactInfo can only be associated with Customer, Partner, or User.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class EmailAddress(ContactInfo):
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.contact_function} - {self.email}"


class PhoneNumber(ContactInfo):
    number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.contact_function} - {self.number}"


class Address(ContactInfo):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.contact_function} - {self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"


class WebPresence(ContactInfo):
    url = models.URLField()

    def __str__(self):
        return f"{self.contact_function} - {self.url}"


class CustomerSetting(models.Model):
    """Per-customer key/value configuration (e.g. dedup_window_seconds=300)."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='settings')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=500)

    class Meta:
        unique_together = [('customer', 'key')]

    def __str__(self):
        return f"{self.customer} · {self.key}={self.value}"

    @classmethod
    def get(cls, customer, key, default=None):
        try:
            return cls.objects.get(customer=customer, key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, customer, key, value):
        obj, _ = cls.objects.update_or_create(
            customer=customer, key=key,
            defaults={'value': str(value)},
        )
        return obj
