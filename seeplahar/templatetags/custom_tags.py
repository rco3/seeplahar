import logging
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()
logger = logging.getLogger(__name__)

@register.filter
def contact_info(contact):
    return contact.email or contact.phone_number or 'No contact info'


# In your_app/templatetags/custom_tags.py


@register.filter(name='getattribute')
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""
    try:
        if isinstance(value, str):
            return f"Error: Received string '{value}' instead of object"
        result = getattr(value, str(arg))
        return result
    except AttributeError as e:
        return f"AttributeError: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


@register.filter(name='type_of')
def type_of(value):
    return type(value).__name__