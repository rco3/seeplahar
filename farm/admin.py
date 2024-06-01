from django.contrib import admin
from .models import Event, Harvest, Plant, SeedLot, SeedlingBatch

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('type', 'date', 'description', 'related_item')
    list_filter = ('date', 'type')

@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ('get_plants', 'date', 'quantity', 'units')
    list_filter = ('date',)

    def get_plants(self, obj):
        return ", ".join([str(plant) for plant in obj.plants.all()])
    get_plants.short_description = 'Plants'


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('variety', 'location', 'source', 'date')
    list_filter = ('date',)

@admin.register(SeedLot)
class SeedLotAdmin(admin.ModelAdmin):
    list_display = ('variety', 'source', 'quantity', 'units')
    list_filter = ('variety',)

@admin.register(SeedlingBatch)
class SeedlingBatchAdmin(admin.ModelAdmin):
    list_display = ('source', 'variety', 'quantity', 'units', 'date')
    list_filter = ('date',)
