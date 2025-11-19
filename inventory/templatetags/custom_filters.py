from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, None)



@register.filter
def num_range(value):
    """Return range 1..value inclusive"""
    return range(1, value+1)


@register.filter
def peso_format(value):
    if not value:
        return "₱0.00"

    # Convert to string and remove peso/comma formatting
    value = str(value).replace("₱", "").replace(",", "")

    try:
        value = float(value)
        return "₱{:,.2f}".format(value)
    except:
        return value


@register.filter
def index(sequence, position):
    """Access list item by index"""
    try:
        return sequence[int(position)]
    except (IndexError, TypeError, ValueError):
        return ""