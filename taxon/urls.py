from django.urls import path
from django.views.generic import RedirectView
from .views import (
    TaxonListView, VarietyListView, VarietyCreateView, CharacteristicNameAutoComplete,
    CharacteristicValueAutoComplete, test_autocomplete, TaxonDeleteView, add_characteristic_form, VarietyDeleteView
)
from seeplahar.views.generic import GenericDetailView, GenericCreateView, GenericUpdateView, GenericDeleteView
from .models import Taxon, Variety
from .forms import TaxonForm, VarietyForm

app_name = 'taxon'

urlpatterns = [
    path('variety/<uuid:pk>/', GenericDetailView.as_view(model=Variety, template_name='taxon/variety_detail.html'),
         name='variety_detail'),
    path('taxon/<uuid:pk>/', GenericDetailView.as_view(model=Taxon, template_name='taxon/taxon_detail.html'),
         name='taxon_detail'),
    path('<str:type>/<uuid:taxon_id>/', VarietyListView.as_view(), name='variety_list'),
    path('add_variety/', VarietyCreateView.as_view(), name='variety_create'),
    path('add_taxon/',
         GenericCreateView.as_view(model=Taxon, form_class=TaxonForm, template_name='taxon/taxon_form.html',
                                   success_url='/dashboard/'), name='taxon_create'),
    path('add_characteristic_form/', add_characteristic_form, name='add_characteristic_form'),
    path('characteristic_name_autocomplete/', CharacteristicNameAutoComplete.as_view(),
         name='characteristic_name_autocomplete'),
    path('characteristic_value_autocomplete/', CharacteristicValueAutoComplete.as_view(),
         name='characteristic_value_autocomplete'),
    path('', TaxonListView.as_view(), name='taxon_list'),
    path('<str:type>/', TaxonListView.as_view(), name='taxon_type_list'),
    path('taxa/<str:type>/', RedirectView.as_view(pattern_name='taxon:taxon_type_list'), name='taxon_type_redirect'),

    # Generic view paths
    path('variety/<uuid:pk>/update/', GenericUpdateView.as_view(model=Variety, form_class=VarietyForm),
         name='variety_update'),
    path('variety/<uuid:pk>/delete/', VarietyDeleteView.as_view(), name='variety_delete'),
    path('taxon/<uuid:pk>/update/', GenericUpdateView.as_view(model=Taxon, form_class=TaxonForm), name='taxon_update'),
    path('taxon/<uuid:pk>/delete/', TaxonDeleteView.as_view(), name='taxon_delete'),

    path('test_autocomplete/', test_autocomplete, name='test_autocomplete'),
]