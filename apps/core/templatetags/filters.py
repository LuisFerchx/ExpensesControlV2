# app/templatetags/mi_filtro.py
from django import template
register = template.Library()


@register.filter
def resta(a, b):
    try:
        return float(a) - float(b)
    except:
        return ''
