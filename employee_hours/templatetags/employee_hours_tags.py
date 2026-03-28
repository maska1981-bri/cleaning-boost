from django import template

register = template.Library()


@register.simple_tag
def get_hours(data, emp_id, day):
    key = (emp_id, day)
    row = data.get(key, {})
    return row.get("hours", "")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)