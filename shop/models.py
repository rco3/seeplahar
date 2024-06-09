from django.db import models
import uuid
from farm.models import SeedLot, Harvest, SeedlingBatch
from media.models import Photo


class SeedPackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seed_lot = models.ForeignKey(SeedLot, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Updated to DecimalField
    quantity_units = models.CharField(max_length=50, default='seeds')
    date_packaged = models.DateField()
    description = models.TextField(blank=True, null=True)
    photos = models.ManyToManyField(Photo, blank=True, related_name='seed_packages')


    def __str__(self):
        return f'Seed Package: {self.seed_lot.name} - {self.quantity} {self.quantity_units}'

class ProducePackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Updated to DecimalField
    quantity_units = models.CharField(max_length=50, default='kg')
    date_packaged = models.DateField()
    description = models.TextField(blank=True, null=True)
    photos = models.ManyToManyField(Photo, blank=True, related_name='produce_packages')


    def __str__(self):
        return f'Produce Package: {self.harvest} - {self.quantity} {self.quantity_units}'

class PlantPackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plants = models.ManyToManyField('farm.Plant', related_name='packages')
    date_packaged = models.DateField()
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    seedling_batch = models.ForeignKey(SeedlingBatch, on_delete=models.SET_NULL, null=True, blank=True)
    photos = models.ManyToManyField(Photo, blank=True, related_name='PlantPackages')


    def __str__(self):
        return f'Plant Package created on {self.date_packaged}'
