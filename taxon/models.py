from django.db import models
import uuid
from users.models import CustomerAwareModel
from media.models import Photo

# taxon/models.py


class Characteristic(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ['name', 'customer']

    def __str__(self):
        return self.name


class CharacteristicValue(models.Model):
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    taxon = models.ForeignKey('Taxon', on_delete=models.CASCADE, null=True, blank=True)
    variety = models.ForeignKey('Variety', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = [('characteristic', 'taxon'), ('characteristic', 'variety')]


class Taxon(CustomerAwareModel):
    FRUIT = 'fruit'
    VEGETABLE = 'vegetable'
    HERB = 'herb'
    FLOWER = 'flower'
    GRASS = 'grass'
    SHRUB = 'shrub'
    TREE = 'tree'
    SUCCULENT = 'succulent'
    ANNUAL = 'annual'
    PERENNIAL = 'perennial'
    OTHER = 'other'

    TYPE_CHOICES = [
        (FRUIT, 'Fruit'),
        (VEGETABLE, 'Vegetable'),
        (HERB, 'Herb'),
        (FLOWER, 'Flower'),
        (GRASS, 'Grass'),
        (SHRUB, 'Shrub'),
        (TREE, 'Tree'),
        (SUCCULENT, 'Succulent'),
        (ANNUAL, 'Annual'),
        (PERENNIAL, 'Perennial'),
        (OTHER, 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    species_name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=OTHER)
    description = models.TextField(blank=True, null=True)
    photos = models.ManyToManyField(Photo, blank=True, related_name='taxons')
    characteristics = models.ManyToManyField(Characteristic, through=CharacteristicValue)

    def __str__(self):
        return self.name

    @property
    def hero_image(self):
        """Own most-recent photo, or fall back to the first variety that has one."""
        photo = self.photos.order_by('-uploaded_at').first()
        if photo:
            return photo
        for variety in self.varieties.all():
            photo = variety.photos.order_by('-uploaded_at').first()
            if photo:
                return photo
        return None

    class Meta:
        verbose_name_plural = "Taxa"



class Variety(CustomerAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    taxon = models.ForeignKey(Taxon, related_name='varieties', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    # origin = models.CharField(max_length=100, blank=True, null=True)
    photos = models.ManyToManyField(Photo, blank=True, related_name='varieties')
    characteristics = models.ManyToManyField(Characteristic, through=CharacteristicValue)

    def __str__(self):
        return self.name

    @property
    def hero_image(self):
        return self.photos.order_by('-uploaded_at').first()

    class Meta:
        verbose_name_plural = "Varieties"


