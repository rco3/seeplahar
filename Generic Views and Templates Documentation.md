# Generic Views and Templates Structure Documentation

## Overview

This document outlines the generic views and templates structure implemented in our Django project, including recent
updates for multitenancy support. The system utilizes Django's class-based views, a set of base templates, and custom
mixins to provide a flexible, DRY (Don't Repeat Yourself) approach to handling CRUD (Create, Read, Update, Delete)
operations for multiple models across different apps while ensuring proper customer isolation in a multi-tenant
environment.

## File Structure

```
seeplahar/
├── views/
│   ├── __init__.py
│   ├── base.py
│   ├── generic.p
│   ├── customer_aware_views.py
├── templates/
│   ├── base_list.html
│   ├── base_detail.html
│   ├── base_form.html
│   └── base_confirm_delete.html
users/
├── models.py
├── middleware.py
├── customer_context.py
├── urls.py
└── views.py (empty, using generic views)
```

## Multitenancy Components

### CustomerAwareModel (users/models.py)

Base model for all customer-specific models:

```python
class CustomerAwareModel(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        abstract = True
```

### CustomerContext (users/customer_context.py)

Context manager for setting/clearing current customer:

```python
class CustomerContext:
    def __init__(self, customer):
        self.customer = customer

    def __enter__(self):
        set_current_customer(self.customer)

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_current_customer(None)
```

### CustomerMiddleware (users/middleware.py)

Middleware to set current customer for each request:

```python
class CustomerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            set_current_customer(request.user.customer)
        else:
            set_current_customer(None)
        response = self.get_response(request)
        return response
```

## Generic Views (seeplahar/views/generic.py)

### CustomerAwareViewMixin and CustomerAwareFormMixin (seeplahar/views/customer_aware_views.py)

These mixins provide customer context and form handling for views:

```python
class CustomerAwareViewMixin:
    def dispatch(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser) or not hasattr(request.user, 'customer'):
            raise Http404("No customer context found")
        with CustomerContext(request.user.customer):
            return super().dispatch(request, *args, **kwargs)


class CustomerAwareFormMixin:
    def has_customer_field(self):
        return hasattr(self.model, 'customer')

    def form_valid(self, form):
        if self.has_customer_field():
            if not self.request.user.customer:
                raise ValidationError("User has no associated customer.")
            form.instance.customer = self.request.user.customer
        return super().form_valid(form)

    def get_form_class(self):
        form_class = super().get_form_class()
        if self.has_customer_field() and 'customer' in form_class.base_fields:
            del form_class.base_fields['customer']
        return form_class
```

### GenericModelView

This is the base class for all generic views. It provides common functionality and context data for child views.

Key features:

- Sets `app_name` and `model_name` based on the model's metadata.
- Generates context data including model fields, verbose names, and URL names for different actions.
- Implements customer-aware queryset filtering.

```python
class GenericModelView:
    def dispatch(self, request, *args, **kwargs):
        self.app_name = self.model._meta.app_label
        self.model_name = self.model._meta.model_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ... (context generation logic)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.model != Customer:
            customer = get_current_customer()
            return queryset.filter(customer=customer)
        return queryset
```

### Specific Generic Views

These views inherit from both `GenericModelView`, customer-aware mixins, and their respective base view classes:

```python
class GenericListView(CustomerAwareViewMixin, GenericModelView, BaseListView):
    template_name = 'base_list.html'


class GenericDetailView(CustomerAwareViewMixin, GenericModelView, BaseDetailView):
    template_name = 'base_detail.html'


class GenericCreateView(CustomerAwareViewMixin, CustomerAwareFormMixin, GenericModelView, BaseCreateView):
    template_name = 'base_form.html'


class GenericUpdateView(CustomerAwareViewMixin, CustomerAwareFormMixin, GenericModelView, BaseUpdateView):
    template_name = 'base_form.html'


class GenericDeleteView(CustomerAwareViewMixin, GenericModelView, BaseDeleteView):
    template_name = 'base_confirm_delete.html'

    def get_success_url(self):
        return reverse(f'{self.model._meta.app_label}:{self.model._meta.model_name}_list')
```

## URL Configuration (users/urls.py)

URL patterns use the generic views directly, specifying the model for each view:

```python
from django.urls import path
from seeplahar.views.generic import GenericListView, GenericDetailView, GenericCreateView, GenericUpdateView,
    GenericDeleteView
from .models import User, Partner

app_name = 'users'

urlpatterns = [
    path('user/', GenericListView.as_view(model=User), name='user_list'),
    path('user/<uuid:pk>/', GenericDetailView.as_view(model=User), name='user_detail'),
    path('user/create/', GenericCreateView.as_view(model=User), name='user_create'),
    path('user/<uuid:pk>/update/', GenericUpdateView.as_view(model=User), name='user_update'),
    path('user/<uuid:pk>/delete/', GenericDeleteView.as_view(model=User), name='user_delete'),

    # Similar patterns for Partner model
    # ...
]
```

## Templates

### base_list.html

Used for displaying lists of objects.

Key features:

- Iterates over `object_list`
- Provides links to detail, update, and delete views for each object
- Includes a link to create a new object

### base_detail.html

Used for displaying details of a single object.

Key features:

- Displays all fields of the object
- Provides links to update and delete the object
- Includes a link back to the list view

### base_form.html

Used for both create and update operations.

Key features:

- Renders the form for creating or updating an object
- Adapts its title based on whether it's a create or update operation

### base_confirm_delete.html

Used for confirming object deletion.

Key features:

- Displays a confirmation message
- Provides a form to confirm deletion
- Includes a cancel link back to the detail view

## Usage in Models

To use these generic views and templates, models should:

1. Inherit from `CustomerAwareModel` (except for the Customer model itself).
2. Define `verbose_name` and `verbose_name_plural` in the model's `Meta` class.
3. Implement a `__str__` method for meaningful object representation.

Example:

```python
from django.db import models
from users.models import CustomerAwareModel


class MyModel(CustomerAwareModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'my model'
        verbose_name_plural = 'my models'

    def __str__(self):
        return self.name
```

## Adding a New Model

To add a new model to use these generic views:

1. Create the model in `models.py`, inheriting from `CustomerAwareModel`.
2. Add URL patterns in the app's `urls.py` file, using the generic views.
3. No need to create custom views or templates unless specific functionality is required.

## Customization

If custom behavior is needed:

1. Create a new view class inheriting from the appropriate generic view.
2. Ensure it includes the necessary customer-aware mixins.
3. Override methods as needed.
4. Use the custom view in URL patterns instead of the generic view.

## Testing

When writing tests:

1. Use `reverse()` with the correct URL names (e.g., `'users:user_list'`).
2. Test all CRUD operations for each model.
3. Ensure proper object creation in `setUp()` method of test classes.
4. Use the `BaseIsolationTest` class to test customer isolation for each model:

```python
class MyModelIsolationTest(BaseIsolationTest):
    model = MyModel
    app_name = 'myapp'
```

## Conclusion

This generic views and templates structure, combined with the multitenancy components, provides a scalable, maintainable
approach to handling CRUD operations across multiple models and apps while ensuring proper customer isolation. It
minimizes code duplication, ensures consistency across the project, and enforces data separation in a multi-tenant
environment.