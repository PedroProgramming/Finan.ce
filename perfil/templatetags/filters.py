from django import template

register = template.Library()

@register.filter
def format_value(value):
    return f'{value:.2f}'