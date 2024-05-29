from django.urls import path
from .views import (
    TaxonListView, TaxonDetailView, TaxonCreateView,
    TaxonUpdateView, TaxonDeleteView, FruitListView,
    VegetableListView, HerbListView, FlowerListView
)

app_name = 'taxon'

urlpatterns = [
    path('', TaxonListView.as_view(), name='taxon_list'),
    path('<uuid:pk>/', TaxonDetailView.as_view(), name='taxon_detail'),
    path('create/', TaxonCreateView.as_view(), name='taxon_create'),
    path('<uuid:pk>/update/', TaxonUpdateView.as_view(), name='taxon_update'),
    path('<uuid:pk>/delete/', TaxonDeleteView.as_view(), name='taxon_delete'),
    path('fruits/', FruitListView.as_view(), name='fruit-list'),
    path('vegetables/', VegetableListView.as_view(), name='vegetable-list'),
    path('herbs/', HerbListView.as_view(), name='herb-list'),
    path('flowers/', FlowerListView.as_view(), name='flower-list'),
]
