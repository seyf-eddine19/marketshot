from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Splits a string by a given separator argument"""
    return value.split(arg)