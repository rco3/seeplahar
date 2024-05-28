from django.db import models

class Species(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class CommonName(models.Model):
    name = models.CharField(max_length=200)
    species = models.ManyToManyField(Species, related_name='common_names')

    def __str__(self):
        return self.name

class Variety(models.Model):
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    common_names = models.ManyToManyField(CommonName, related_name='varieties')
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name
