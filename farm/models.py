from django.db import models
import uuid
from users.models import Partner
from datetime import datetime

class SeedLot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variety = models.ForeignKey('taxon.Variety', on_delete=models.CASCADE, related_name='seed_lots')
    name = models.CharField(max_length=100, default='New Seedlot')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Updated to DecimalField
    units = models.CharField(max_length=50, null=True, blank=True)
    date_received = models.DateField(default=datetime.now)
    origin = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.ForeignKey('Harvest', null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return self.name

class Plant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seed_lot = models.ForeignKey(SeedLot, on_delete=models.CASCADE, related_name='plants', null=True, blank=True)
    seedling_batch = models.ForeignKey('SeedlingBatch', on_delete=models.CASCADE, related_name='plants', null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True)
    variety = models.ForeignKey('taxon.Variety', null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now)
    location = models.CharField(max_length=255, null=True, blank=True)
    source = models.ForeignKey('SeedLot', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50, choices=[('growing', 'Growing'), ('harvested', 'Harvested'), ('failed', 'Failed')], default=('growing', 'Growing'))

    def __str__(self):
        return f'{self.variety.name} - {self.location}'


class Harvest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plants = models.ManyToManyField('Plant', related_name='harvests')
    date = models.DateField(default=datetime.now)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    units = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Harvest on {self.date}'


class SeedlingBatch(models.Model):
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

    def __str__(self):
        return f'{self.seed_lot.name} batch sown on {self.date}'


class Event(models.Model):
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
    related_item = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Event: {self.type} on {self.date}'
