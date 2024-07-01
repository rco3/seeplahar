from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.contenttypes.models import ContentType
from .models import Customer, Partner, User, Address, PhoneNumber, EmailAddress, WebPresence, ContactInfoType


class BaseAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return self.filter_queryset_for_non_superuser(request, qs)

    def filter_queryset_for_non_superuser(self, request, qs):
        # This method should be overridden in subclasses
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            kwargs = self.filter_foreign_key_for_non_superuser(request, db_field, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def filter_foreign_key_for_non_superuser(self, request, db_field, kwargs):
        # This method should be overridden in subclasses
        return kwargs


class CustomerAwareAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(customer=request.user.customer)
        return qs

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True  # Allow access to the changelist
        return request.user.is_superuser or obj.customer == request.user.customer

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return True  # Allow access to the changelist
        return request.user.is_superuser or obj.customer == request.user.customer

    def save_model(self, request, obj, form, change):
        if not change:  # Only set the customer for new objects
            obj.customer = request.user.customer
        super().save_model(request, obj, form, change)


class BaseContactAdmin(CustomerAwareAdmin):
    list_display = ('get_entity_type', 'get_entity_name', 'contact_function', 'customer')
    list_filter = ('content_type', 'contact_function', 'customer')
    search_fields = ('content_object__name', 'customer__name')

    def get_entity_type(self, obj):
        return obj.content_type.model.capitalize()
    get_entity_type.short_description = 'Entity Type'

    def get_entity_name(self, obj):
        return str(obj.content_object)
    get_entity_name.short_description = 'Entity Name'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type" and not request.user.is_superuser:
            kwargs["queryset"] = ContentType.objects.filter(
                model__in=['customer', 'partner', 'user']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Customer)
class CustomerAdmin(BaseAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

    def filter_queryset_for_non_superuser(self, request, qs):
        return qs.filter(id=request.user.customer.id)


@admin.register(Partner)
class PartnerAdmin(CustomerAwareAdmin):
    list_display = ('name', 'customer', 'is_active')
    search_fields = ('name', 'customer__name')
    list_filter = ('is_active', 'customer')


@admin.register(User)
class UserAdmin(CustomerAwareAdmin, DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'customer', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'customer__name')
    list_filter = ('is_staff', 'is_superuser', 'customer')

    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Customer Info', {'fields': ('customer',)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Customer Info', {'fields': ('customer',)}),
    )


@admin.register(EmailAddress)
class EmailAddressAdmin(BaseContactAdmin):
    list_display = BaseContactAdmin.list_display + ('email', 'is_primary', 'is_verified')
    search_fields = BaseContactAdmin.search_fields + ('email',)


@admin.register(PhoneNumber)
class PhoneNumberAdmin(BaseContactAdmin):
    list_display = BaseContactAdmin.list_display + ('number',)
    search_fields = BaseContactAdmin.search_fields + ('number',)


@admin.register(Address)
class AddressAdmin(BaseContactAdmin):
    list_display = BaseContactAdmin.list_display + ('street', 'city', 'state', 'postal_code', 'country')
    search_fields = BaseContactAdmin.search_fields + ('street', 'city', 'state', 'postal_code', 'country')


@admin.register(WebPresence)
class WebPresenceAdmin(BaseContactAdmin):
    list_display = BaseContactAdmin.list_display + ('url',)
    search_fields = BaseContactAdmin.search_fields + ('url',)


@admin.register(ContactInfoType)
class ContactInfoTypeAdmin(CustomerAwareAdmin):
    list_display = ('name', 'customer')
    search_fields = ('name', 'customer__name')
    list_filter = ('customer',)