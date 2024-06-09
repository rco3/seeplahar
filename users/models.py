from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class SiteUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=30, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True)
    organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.SET_NULL, related_name='members')

    def __str__(self):
        return self.username or self.email  # Use username if available, else email


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    contact_info = models.ManyToManyField('ContactInfo', related_name='organizations')

    def __str__(self):
        return self.name


class ContactInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_choices = [
        ('delivery', 'Delivery'),
        ('accounts_payable', 'Accounts Payable'),
        ('billing', 'Billing'),
        ('other', 'Other'),
    ]
    type = models.CharField(max_length=50, choices=type_choices)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    site_user = models.ForeignKey('SiteUser', null=True, blank=True, on_delete=models.CASCADE, related_name='contact_info')

    def __str__(self):
        return f"{self.type} - {self.email or self.phone_number or 'No contact info'}"
