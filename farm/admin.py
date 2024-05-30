from django.contrib import admin
from .models import SeedLot, SeedlingBatch, Plant, Harvest, Event

@admin.register(SeedLot)
class SeedLotAdmin(admin.ModelAdmin):
    list_display = ('variety', 'quantity', 'date_received')
    search_fields = ('variety__name', 'quantity', 'date_received')
    list_filter = ('date_received',)
    fields = ('variety', 'quantity', 'date_received', 'photos')

@admin.register(SeedlingBatch)
class SeedlingBatchAdmin(admin.ModelAdmin):
    list_display = ('seed_lot', 'quantity', 'sowing_date')
    search_fields = ('seed_lot__variety__name', 'quantity', 'sowing_date')
    list_filter = ('sowing_date',)
    fields = ('seed_lot', 'quantity', 'sowing_date', 'photos')

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('seed_lot', 'seedling_batch', 'planting_date', 'location')
    search_fields = ('seed_lot__variety__name', 'seedling_batch__seed_lot__variety__name', 'planting_date', 'location')
    list_filter = ('planting_date', 'location')
    fields = ('seed_lot', 'seedling_batch', 'planting_date', 'location', 'photos')

@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ('plant', 'harvest_date', 'quantity')
    search_fields = ('plant__seed_lot__variety__name', 'harvest_date', 'quantity')
    list_filter = ('harvest_date',)
    fields = ('plant', 'harvest_date', 'quantity', 'photos')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_date', 'plant', 'seed_lot', 'seedling_batch', 'harvest')
    search_fields = ('event_type', 'event_date', 'plant__seed_lot__variety__name', 'seed_lot__variety__name', 'seedling_batch__seed_lot__variety__name', 'harvest__plant__seed_lot__variety__name')
    list_filter = ('event_date', 'event_type')
    fields = ('event_type', 'description', 'event_date', 'plant', 'seed_lot', 'seedling_batch', 'harvest')
