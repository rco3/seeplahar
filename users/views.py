from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import SiteUser, Organization

class SiteUserListView(ListView):
    model = SiteUser
    template_name = 'users/siteuser_list.html'
    context_object_name = 'siteusers'

class SiteUserDetailView(DetailView):
    model = SiteUser
    template_name = 'users/siteuser_detail.html'
    context_object_name = 'siteuser'

class OrganizationListView(ListView):
    model = Organization
    template_name = 'users/organization_list.html'
    context_object_name = 'organizations'

class OrganizationDetailView(DetailView):
    model = Organization
    template_name = 'users/organization_detail.html'
    context_object_name = 'organization'
