from django.contrib import admin
from .models import Taxon, Variety, Synonym, Photo, Characteristic


class CharacteristicInline(admin.StackedInline):
    model = Characteristic
    extra = 1


@admin.register(Variety)
class VarietyAdmin(admin.ModelAdmin):
    inlines = [CharacteristicInline]
    list_display = ('name', 'taxon', 'description')
    search_fields = ('name', 'taxon__name')
    list_filter = ('taxon', 'description')


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'variety')
    search_fields = ('name', 'value', 'variety__name')
    list_filter = ('name', 'value')


@admin.register(Taxon)
class TaxonAdmin(admin.ModelAdmin):
    list_display = ('name', 'species_name', 'type', 'description')
    search_fields = ('name', 'species_name', 'type')
    list_filter = ('type',)
    fields = ('name', 'species_name', 'type', 'description', 'photos')


@admin.register(Synonym)
class SynonymAdmin(admin.ModelAdmin):
    list_display = ('name', 'taxon')
    search_fields = ('name', 'taxon__name')
    list_filter = ('taxon',)
    fields = ('name', 'taxon')
