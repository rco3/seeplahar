"""
URL configuration for Seeplahar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views.specific import (
    HomePageView, custom_logout, CustomLoginView, DashboardView
)
from .views.generic import (
    GenericListView, GenericDetailView, GenericCreateView, GenericUpdateView, GenericDeleteView
)
from autocomplete import HTMXAutoComplete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path("__reload__/", include("django_browser_reload.urls")),
    path('taxon/', include('taxon.urls', namespace='taxon')),
    path('farm/', include('farm.urls', namespace='farm')),
    # path('shop/', include('shop.urls', namespace='shop')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('<uuid:pk>/', GenericDetailView.as_view(), name='generic-detail'),
    path('users/', include('users.urls', namespace='users')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    *HTMXAutoComplete.url_dispatcher('ac'),

    # New generic URL patterns
    path('<str:app_name>/<str:model_name>/', GenericListView.as_view(), name='generic_list'),
    path('<str:app_name>/<str:model_name>/create/', GenericCreateView.as_view(), name='generic_create'),
    path('<str:app_name>/<str:model_name>/<uuid:pk>/', GenericDetailView.as_view(), name='generic_detail'),
    path('<str:app_name>/<str:model_name>/<uuid:pk>/update/', GenericUpdateView.as_view(), name='generic_update'),
    path('<str:app_name>/<str:model_name>/<uuid:pk>/delete/', GenericDeleteView.as_view(), name='generic_delete'),
]