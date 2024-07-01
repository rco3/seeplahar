from django.db import models
import uuid
from users.models import Partner
from users.models import CustomerAwareModel
from datetime import datetime
from media.models import Photo
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# farm/models.py

class SeedLot(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variety = models.ForeignKey('taxon.Variety', on_delete=models.CASCADE, related_name='seed_lots')
    name = models.CharField(max_length=100, default='New Seedlot')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Updated to DecimalField
    units = models.CharField(max_length=50, null=True, blank=True)
    date_received = models.DateField(null=True, blank=True, default=datetime.now)
    origin = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    source_partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name='sourced_seedlots')
    source = models.ForeignKey('Harvest', null=True, blank=True, on_delete=models.SET_NULL)
    photos = models.ManyToManyField(Photo, blank=True, related_name='seed_lots')


    def __str__(self):
        return self.name


class Planting(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name='sourced_plantings')
    variety = models.ForeignKey('taxon.Variety', null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now)
    location = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('growing', 'Growing'), ('harvested', 'Harvested'), ('failed', 'Failed')], default='growing')
    photos = models.ManyToManyField(Photo, blank=True, related_name='plantings')
    quantity = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=50, choices=[('mound', 'Mound'), ('row', 'Row'), ('raised_bed', 'Raised Bed'), ('container', 'Container'), ('pot', 'Pot')], default='container')

    # Generic Foreign Key to link to the source
    source_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True, blank=True, limit_choices_to=models.Q(app_label='farm', model__in=['seedlot', 'seedlingbatch', 'planting']))
    source_object_id = models.UUIDField(null=True, blank=True)
    source = GenericForeignKey('source_content_type', 'source_object_id')

    def __str__(self):
        return f'{self.variety.name} - {self.location} ({self.quantity})'


class Location(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class Harvest(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plants = models.ManyToManyField('Planting', related_name='harvests')
    date = models.DateField(default=datetime.now)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    units = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    photos = models.ManyToManyField(Photo, blank=True, related_name='harvests')
    source_partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name='sourced_harvests')
    # organization represents the external source from which the Item was obtained
    def __str__(self):
        return f'Harvest on {self.date}'


class SeedlingBatch(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seed_lot = models.ForeignKey(SeedLot, on_delete=models.CASCADE, related_name='seedling_batches')
    date = models.DateField(default=datetime.now)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Updated to DecimalField
    units = models.CharField(max_length=50, default='seeds')
    location = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('germinating', 'Germinating'), ('transplanted', 'Transplanted'), ('failed', 'Failed')], default=('germinating', 'Germinating'))
    parent_batch = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_batches')
    source = models.ForeignKey('SeedLot', null=True, blank=True, on_delete=models.SET_NULL)
    variety = models.ForeignKey('taxon.Variety', null=True, blank=True, on_delete=models.SET_NULL)
    photos = models.ManyToManyField(Photo, blank=True, related_name='seedlingBatches')


    def __str__(self):
        return f'{self.seed_lot.name} batch sown on {self.date}'


class Event(CustomerAwareModel):
    EVENT_TYPES = [
        ('collection', 'Collection'),
        ('fermentation_start', 'Fermentation Start'),
        ('fermentation_end', 'Fermentation End'),
        ('storage', 'Storage'),
        ('planting', 'Planting'),
        ('germination', 'Germination'),
        ('first_true_leaves', 'First True Leaves'),
        ('transplant', 'Transplant'),
        ('watering', 'Watering'),
        ('fertilizing', 'Fertilizing'),
        ('pruning', 'Pruning'),
        ('treatment', 'Treatment'),
        ('packaging', 'Packaging'),
        ('sale', 'Sale'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=EVENT_TYPES, default='collection')
    date = models.DateField(default=datetime.now)
    description = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    related_item = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'Event: {self.type} on {self.date}'
