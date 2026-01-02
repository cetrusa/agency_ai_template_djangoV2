from django import template
import json
from dataclasses import asdict, is_dataclass

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def to_json(value):
    if is_dataclass(value):
        return json.dumps(asdict(value))
    return json.dumps(value)
