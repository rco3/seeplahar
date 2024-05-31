from django.urls import path
from .views import (
    TaxonListView, VarietyDetailView, VarietyListView, TaxonDetailView
)
import uuid

app_name = 'taxon'

urlpatterns = [
    path('<str:type>/', TaxonListView.as_view(), name='taxon-list'),
    path('<str:type>/<uuid:taxon_id>/', VarietyListView.as_view(), name='variety-list'),
    path('variety/<uuid:pk>/', VarietyDetailView.as_view(), name='variety-detail'),
    path('taxon/<uuid:pk>/', TaxonDetailView.as_view(), name='taxon-detail'),
]
