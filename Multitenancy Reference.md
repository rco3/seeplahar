# Multitenancy Implementation Reference

## Core Components

1. CustomerAwareModel
   - Base model for all customer-specific models
   - Includes non-nullable ForeignKey to Customer
   - Custom save method to set customer if not provided

2. CustomerContext
   - Manages customer context using thread-local storage
   - Provides set_current_customer(), get_current_customer(), clear_current_customer()

3. CustomerMiddleware
   - Sets current customer for each request based on authenticated user
   - Clears customer context after response is generated

4. CustomerAwareViewMixin
   - Ensures correct customer context in views
   - Raises Http404 if no valid customer context is found

5. CustomerAwareFormMixin
   - Automatically sets customer for new objects based on customer context
   - Removes customer field from forms
   - Raises ValidationError if no valid customer context is found

6. Generic Views
   - Use CustomerAwareViewMixin and CustomerAwareFormMixin
   - Filter querysets based on current customer context

7. Queryset Filtering
   - Implemented in GenericModelView to ensure users only see their customer's objects

8. BaseIsolationTest
   - Base test class for customer isolation testing
   - Simulates middleware behavior

## Key Features

- Automatic customer assignment for new objects
- Query filtering to return only current customer's objects
- View-level and form-level customer enforcement
- Middleware integration for request-level customer context
- Flexible context management with CustomerContext
- Comprehensive testing framework

## Implementation Details

- CustomerAwareModel includes `customer = models.ForeignKey(Customer, on_delete=models.CASCADE)`
- CustomerContext uses thread-local storage for context management
- CustomerMiddleware sets and clears customer context for each request
- CustomerAwareViewMixin checks for valid customer context in dispatch method
- CustomerAwareFormMixin uses customer context for object creation and form customization
- Generic views inherit from mixins and base view classes
- Queryset filtering uses `filter(customer=get_current_customer())`
- BaseIsolationTest includes separate methods for testing each CRUD operation

This implementation ensures strict customer data isolation at multiple levels of the application, from database to view layer.