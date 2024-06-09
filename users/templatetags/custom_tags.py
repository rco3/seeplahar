from django import template

register = template.Library()

@register.filter
def contact_info(contact):
    return contact.email or contact.phone_number or 'No contact info'
