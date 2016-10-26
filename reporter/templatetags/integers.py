from django import template

register = template.Library()

@register.filter
def hexadecimal(value):
    if value == '':
        return value;
    if(int(value)==value):
        return hex(int(value))[2:]
    else:
        return value