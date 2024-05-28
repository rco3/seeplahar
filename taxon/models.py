from django.db import models
import uuid


class Taxon(models.Model):
    FRUIT = 'fruit'
    VEGETABLE = 'vegetable'
    HERB = 'herb'
    FLOWER = 'flower'
    GRASS = 'grass'
    SHRUB = 'shrub'
    TREE = 'tree'
    CACTUS = 'cactus'
    OTHER = 'other'

    TYPE_CHOICES = [
        (FRUIT, 'Fruit'),
        (VEGETABLE, 'Vegetable'),
        (HERB, 'Herb'),
        (FLOWER, 'Flower'),
        (GRASS, 'Grass'),
        (SHRUB, 'Shrub'),
        (TREE, 'Tree'),
        (CACTUS, 'Cactus'),
        (OTHER, 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    species_name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=OTHER)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Synonym(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    taxon = models.ForeignKey(Taxon, related_name='synonyms', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Variety(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    # taxon = models.ForeignKey(Taxon, related_name='varieties', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name
