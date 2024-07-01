from django.contrib import admin
from .models import Event, Harvest, Planting, SeedLot, SeedlingBatch
from users.admin import CustomerAwareAdmin

@admin.register(Event)
class EventAdmin(CustomerAwareAdmin):
    list_display = ('type', 'date', 'description', 'related_item')
    list_filter = ('date', 'type')

@admin.register(Harvest)
class HarvestAdmin(CustomerAwareAdmin):
    list_display = ('get_plants', 'date', 'quantity', 'units')
    list_filter = ('date',)

    def get_plants(self, obj):
        return ", ".join([str(planting) for planting in obj.plants.all()])
    get_plants.short_description = 'Plants'


@admin.register(Planting)
class PlantAdmin(CustomerAwareAdmin):
    list_display = ('variety', 'location', 'source', 'date')
    list_filter = ('date',)

@admin.register(SeedLot)
class SeedLotAdmin(CustomerAwareAdmin):
    list_display = ('variety', 'source', 'quantity', 'units')
    list_filter = ('variety',)

@admin.register(SeedlingBatch)
class SeedlingBatchAdmin(CustomerAwareAdmin):
    list_display = ('source', 'variety', 'quantity', 'units', 'date')
    list_filter = ('date',)
