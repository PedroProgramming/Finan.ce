from django import template

register = template.Library()

@register.filter
def calcular_percentual_total(value, total):
    total_percentual = (value * 100) / total
    return int(total_percentual)
