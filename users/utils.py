# users/utils.py

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import ContactInfoType, EmailAddress

User = get_user_model()


@transaction.atomic
def create_user_with_email(username, email, password, customer, is_staff=True, **extra_fields):
    user = User.objects.create_user(username, password=password, customer=customer, is_staff=is_staff, **extra_fields)

    user.is_staff = True
    user.save()

    contact_function, created = ContactInfoType.objects.get_or_create(
        name="Primary Email",
        customer=customer,
    )

    EmailAddress.objects.create(
        customer=customer,
        content_type=ContentType.objects.get_for_model(User),
        object_id=user.id,
        contact_function=contact_function,
        email=email,
        is_primary=True,
        is_verified=False
    )

    return user