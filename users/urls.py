from django.urls import path
from seeplahar.views.generic import GenericListView, GenericDetailView, GenericCreateView, GenericUpdateView, \
    GenericDeleteView
from .models import User, Partner

app_name = 'users'

urlpatterns = [
    # User URLs
    path('user/', GenericListView.as_view(model=User), name='user_list'),
    path('user/<uuid:pk>/', GenericDetailView.as_view(model=User), name='user_detail'),
    path('user/create/', GenericCreateView.as_view(
        model=User,
        fields=['username', 'password', 'customer', 'is_staff', 'is_superuser']
    ), name='user_create'),
    path('user/<uuid:pk>/update/', GenericUpdateView.as_view(
        model=User,
        fields=['username', 'customer', 'is_staff', 'is_superuser']
    ), name='user_update'),
    path('user/<uuid:pk>/delete/', GenericDeleteView.as_view(model=User), name='user_delete'),

    # Partner URLs
    path('partner/', GenericListView.as_view(model=Partner), name='partner_list'),
    path('partner/<uuid:pk>/', GenericDetailView.as_view(model=Partner), name='partner_detail'),
    path('partner/create/', GenericCreateView.as_view(
        model=Partner,
        fields=['name', 'customer']
    ), name='partner_create'),
    path('partner/<uuid:pk>/update/', GenericUpdateView.as_view(
        model=Partner,
        fields=['name', 'customer']
    ), name='partner_update'),
    path('partner/<uuid:pk>/delete/', GenericDeleteView.as_view(model=Partner), name='partner_delete'),
]