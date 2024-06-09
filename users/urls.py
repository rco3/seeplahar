from django.urls import path
from .views import SiteUserListView, SiteUserDetailView, OrganizationListView, OrganizationDetailView

app_name = 'users'

urlpatterns = [
    path('siteusers/', SiteUserListView.as_view(), name='siteuser_list'),
    path('siteusers/<uuid:pk>/', SiteUserDetailView.as_view(), name='siteuser_detail'),
    path('organizations/', OrganizationListView.as_view(), name='organization_list'),
    path('organizations/<uuid:pk>/', OrganizationDetailView.as_view(), name='organization_detail'),
]
