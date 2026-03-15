from django.db import models
import uuid

from farm.utils.naming import generate_entity_name
from users.models import Partner
from users.models import CustomerAwareModel
from datetime import datetime
from media.models import Photo
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# farm/models.py


class SeedLot(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variety = models.ForeignKey('taxon.Variety', on_delete=models.CASCADE, related_name='seed_lots')
    name = models.CharField(max_length=100, default='New Seedlot')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    units = models.CharField(max_length=50, null=True, blank=True)
    date_received = models.DateField(null=True, blank=True, default=datetime.now)
    vendor = models.CharField(max_length=100, null=True, blank=True)  # Changed from 'origin'
    description = models.TextField(blank=True, null=True)

    # Commercial source (who's responsible for quality)
    source_partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='sourced_seedlots')

    # Biological source (what it came from) - GenericFK
    source_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True,
                                            limit_choices_to=models.Q(app_label='farm',
                                                                      model__in=['harvest', 'planting', 'seedlot']))
    source_object_id = models.UUIDField(null=True, blank=True)
    source = GenericForeignKey('source_content_type', 'source_object_id')

    location = models.ForeignKey(
        'Location', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='seed_lots',
    )
    photos = models.ManyToManyField(Photo, blank=True, related_name='seed_lots')

    def __str__(self):
        return self.name

    def current_status(self):
        """Get the most recent event for this seedlot"""
        latest_event = Event.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        ).order_by('-date').first()
        return latest_event.type if latest_event else 'received'

    def generate_name(self):
        """Generate a proper seedlot name using variety and source"""
        variety_name = self.variety.name if self.variety else 'Unknown'

        if self.source_partner:
            source_name = self.source_partner.name
        elif self.vendor:
            source_name = self.vendor
        else:
            source_name = 'Unknown'

        return generate_entity_name(variety_name, source_name, SeedLot, self.customer)

    def save(self, *args, **kwargs):
        # Auto-generate name if it's the terrible default or empty
        if not self.name or self.name == 'New Seedlot':
            self.name = self.generate_name()
        super().save(*args, **kwargs)

class Planting(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name='sourced_plantings')
    variety = models.ForeignKey('taxon.Variety', null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now)
    location = models.ForeignKey(
        'Location', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='plantings',
    )
    status = models.CharField(max_length=50, choices=[('growing', 'Growing'), ('harvested', 'Harvested'), ('failed', 'Failed')], default='growing')
    photos = models.ManyToManyField(Photo, blank=True, related_name='plantings')
    quantity = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=50, choices=[('mound', 'Mound'), ('row', 'Row'), ('raised_bed', 'Raised Bed'), ('container', 'Container'), ('pot', 'Pot')], default='container')

    # Generic Foreign Key to link to the source
    source_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True, blank=True, limit_choices_to=models.Q(app_label='farm', model__in=['seedlot', 'seedlingbatch', 'planting']))
    source_object_id = models.UUIDField(null=True, blank=True)
    source = GenericForeignKey('source_content_type', 'source_object_id')

    def __str__(self):
        location_name = self.location.name if self.location else 'No location'
        return f'{self.variety.name} - {location_name} ({self.quantity})'


class Location(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class HarvestContainer(CustomerAwareModel):
    """A physical container (bag, basket, bin, etc.) identified by a UUID label.

    Containers are reusable. History is reconstructed by querying all Harvests
    that reference this container via Harvest.container FK.
    """
    CONTAINER_TYPES = [
        ('bag', 'Bag'),
        ('basket', 'Basket'),
        ('bin', 'Bin'),
        ('jug', 'Jug'),
        ('tray', 'Tray'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('dispatched', 'Dispatched'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    container_type = models.CharField(max_length=50, choices=CONTAINER_TYPES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stored_containers',
    )

    def __str__(self):
        return self.name if self.name else f"{self.get_container_type_display()} ({str(self.id)[:8]})"

    @property
    def history(self):
        """All harvests ever associated with this container, newest first."""
        return list(Harvest.objects.filter(container=self).order_by('-date'))


class Harvest(CustomerAwareModel):
    STATUS_CHOICES = [
        ('placeholder', 'Placeholder'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plants = models.ManyToManyField('Planting', related_name='harvests')
    variety = models.ForeignKey('taxon.Variety', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=datetime.now)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    units = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    container = models.ForeignKey(
        'HarvestContainer', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='harvests',
    )
    photos = models.ManyToManyField(Photo, blank=True, related_name='harvests')
    source_partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name='sourced_harvests')

    def __str__(self):
        return f'Harvest on {self.date}'


# farm/models.py - Updated SeedlingBatch model

# farm/models.py - Updated SeedlingBatch model

class SeedlingBatch(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variety = models.ForeignKey('taxon.Variety', null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(default=datetime.now)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    units = models.CharField(max_length=50, default='seeds')
    parent_batch = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='child_batches')

    # Standardized source pattern
    vendor = models.CharField(max_length=100, null=True, blank=True)
    source_partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='sourced_seedling_batches')
    source_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True,
                                            limit_choices_to=models.Q(app_label='farm',
                                                                      model__in=['seedlot', 'planting',
                                                                                 'seedlingbatch']))
    source_object_id = models.UUIDField(null=True, blank=True)
    source = GenericForeignKey('source_content_type', 'source_object_id')
    location = models.ForeignKey(
        'Location', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='seedling_batches',
    )

    photos = models.ManyToManyField(Photo, blank=True, related_name='seedling_batches')

    def __str__(self):
        if self.variety:
            return f'{self.variety.name} batch sown on {self.date}'
        return f'SeedlingBatch sown on {self.date}'

    def current_status(self):
        """Get the most recent event for this seedling batch"""
        latest_event = Event.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        ).order_by('-date').first()
        return latest_event.type if latest_event else 'sown'


# farm/models.py - Updated Event model

class Event(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50)  # Free text - no hard-coded choices!
    date = models.DateField(default=datetime.now)
    description = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    related_item = GenericForeignKey('content_type', 'object_id')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='events_performed',
    )

    def __str__(self):
        return f'Event: {self.type} on {self.date}'