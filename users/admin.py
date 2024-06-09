from django.contrib import admin
from .models import SiteUser, Organization, ContactInfo


@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'organization')
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('type', 'email', 'phone_number', 'site_user')
    search_fields = ('email', 'phone_number', 'site_user__email')
