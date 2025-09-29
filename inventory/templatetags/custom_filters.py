from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, None)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def num_range(value):
    """Return range 1..value inclusive"""
    return range(1, value+1)