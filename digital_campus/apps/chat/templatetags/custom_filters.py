from django import template

register = template.Library()

@register.filter
def endswith(value, suffix):
    return str(value).lower().endswith(suffix)