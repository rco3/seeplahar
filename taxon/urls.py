from django.urls import path
from .views import (
    TaxonListView, TaxonDetailView, TaxonCreateView, TaxonUpdateView, TaxonDeleteView
)

urlpatterns = [
    path('', TaxonListView.as_view(), name='taxon_list'),
    path('<uuid:pk>/', TaxonDetailView.as_view(), name='taxon_detail'),
    path('create/', TaxonCreateView.as_view(), name='taxon_create'),
    path('<uuid:pk>/update/', TaxonUpdateView.as_view(), name='taxon_update'),
    path('<uuid:pk>/delete/', TaxonDeleteView.as_view(), name='taxon_delete'),
]
