import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(needs_autoescape=True)
def extradata(value, autoescape=True):
    data = json.loads(value)
    ret = ''
    for d in data['data']:
        ret += '<tr><td>'+d['text']+'</td><td>'+d['value']+'</td></tr>'
    return mark_safe(ret)