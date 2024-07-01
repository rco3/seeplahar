from django.urls import path
from .views import (
    TaxonListView, VarietyDetailView, VarietyListView, TaxonDetailView, TaxonTestListView, VarietyCreateView,
    TaxonCreateView, SynonymCreateView, CharacteristicNameAutoComplete, CharacteristicValueAutoComplete,
    add_characteristic_form, test_autocomplete
)
import uuid

# taxon/urls.py

app_name = 'taxon'

urlpatterns = [
    path('variety/<uuid:pk>/', VarietyDetailView.as_view(), name='variety-detail'),
    path('taxon/<uuid:pk>/', TaxonDetailView.as_view(), name='taxon-detail'),
    path('<str:type>/<uuid:taxon_id>/', VarietyListView.as_view(), name='variety-list'),
    path('add_variety/', VarietyCreateView.as_view(), name='variety_create'),
    path('add_taxon/', TaxonCreateView.as_view(), name='taxon_create'),
    path('add_synonym/', SynonymCreateView.as_view(), name='synonym_create'),
    path('add_characteristic_form/', add_characteristic_form, name='add_characteristic_form'),
    path('characteristic-name-autocomplete/', CharacteristicNameAutoComplete.as_view(), name='characteristicNameAutoComplete'),
    path('characteristic-value-autocomplete/', CharacteristicValueAutoComplete.as_view(), name='characteristicValueAutoComplete'),
    path('<str:type>/', TaxonListView.as_view(), name='taxon-list'),

]
