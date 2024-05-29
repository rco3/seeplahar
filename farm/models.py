import uuid
from django.db import models
from taxon.models import Variety, Photo  # Assuming Variety is defined in the taxon app

class SeedLot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date_received = models.DateField()
    photos = models.ManyToManyField(Photo, blank=True, related_name='seedlots')

    def __str__(self):
        return f"{self.variety.name} ({self.quantity})"

class SeedlingBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seed_lot = models.ForeignKey(SeedLot, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sowing_date = models.DateField()
    photos = models.ManyToManyField(Photo, blank=True, related_name='seedlingbatches')

    def __str__(self):
        return f"SeedlingBatch from {self.seed_lot.variety.name} ({self.quantity})"

class Plant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seed_lot = models.ForeignKey(SeedLot, on_delete=models.CASCADE, null=True, blank=True)
    seedling_batch = models.ForeignKey(SeedlingBatch, on_delete=models.CASCADE, null=True, blank=True)
    planting_date = models.DateField()
    location = models.CharField(max_length=200)
    photos = models.ManyToManyField(Photo, blank=True, related_name='plants')

    def __str__(self):
        return f"Plant from {self.seed_lot.variety.name} planted on {self.planting_date}"

class Harvest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    harvest_date = models.DateField()
    quantity = models.IntegerField()
    photos = models.ManyToManyField(Photo, blank=True, related_name='harvests')

    def __str__(self):
        return f"Harvest from {self.plant.seed_lot.variety.name} on {self.harvest_date} ({self.quantity})"

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50)  # e.g., Planting, Watering, Fertilizing, etc.
    description = models.TextField()
    event_date = models.DateField()
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, null=True, blank=True)
    seed_lot = models.ForeignKey(SeedLot, on_delete=models.CASCADE, null=True, blank=True)
    seedling_batch = models.ForeignKey(SeedlingBatch, on_delete=models.CASCADE, null=True, blank=True)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.event_type} on {self.event_date}"
