import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from users.models import CustomerAwareModel


def customer_photo_path(instance, filename):
    # Get first 4 of customer name (lowercase, alphanumeric only)
    customer_prefix = ''.join(c.lower() for c in instance.customer.name if c.isalnum())[:4]
    # Get last 8 of UUID
    uuid_suffix = str(instance.customer.id)[-8:]
    # Return path like "photos/gala_12345678/filename"
    return f'{customer_prefix}_{uuid_suffix}/{filename}'


class Photo(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to=customer_photo_path)
    description = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.description or str(self.image)
