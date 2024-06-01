# taxon/admin.py
from django.contrib import admin
from .models import Taxon, Variety, Characteristic

class TaxonAdmin(admin.ModelAdmin):
    list_display = ('name', 'species_name', 'type')
    search_fields = ('name', 'species_name', 'type')

class CharacteristicInline(admin.TabularInline):
    model = Variety.characteristics.through
    extra = 1

class VarietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'taxon', 'description')
    search_fields = ('name', 'taxon__name', 'description')
    inlines = [CharacteristicInline]

class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name', 'value')

admin.site.register(Taxon, TaxonAdmin)
admin.site.register(Variety, VarietyAdmin)
admin.site.register(Characteristic, CharacteristicAdmin)
