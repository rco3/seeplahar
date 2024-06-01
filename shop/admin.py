from django.contrib import admin
from .models import SeedPackage, ProducePackage, PlantPackage

admin.site.register(SeedPackage)
admin.site.register(ProducePackage)
admin.site.register(PlantPackage)
