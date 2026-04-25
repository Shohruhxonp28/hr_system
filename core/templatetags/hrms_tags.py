from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dict by key: {{ mydict|get_item:key }}"""
    if isinstance(dictionary, (dict, set)):
        if isinstance(dictionary, set):
            return key in dictionary
        return dictionary.get(key)
    return None


@register.filter
def in_set(value, obj):
    """Check if value is in a set/list: {{ emp.id|in_set:existing }}"""
    try:
        return value in obj
    except (TypeError, KeyError):
        return False


@register.filter
def format_money(value):
    """Format number as Uzbek currency: 12500000 -> 12 500 000"""
    try:
        value = int(value)
        return f"{value:,}".replace(",", " ")
    except (TypeError, ValueError):
        return value


@register.filter
def minutes_to_hm(minutes):
    """Convert minutes to h:mm format"""
    try:
        m = int(minutes)
        h = m // 60
        rem = m % 60
        if h > 0:
            return f"{h}s {rem}d"
        return f"{rem} daq"
    except (TypeError, ValueError):
        return minutes


@register.filter
def multiply(value, arg):
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except Exception:
        return 0


@register.simple_tag
def attendance_status_color(status):
    colors = {
        'present': 'badge-present',
        'late': 'badge-late',
        'absent': 'badge-absent',
        'day_off': 'badge-day-off',
        'holiday': 'badge-holiday',
        'incomplete': 'badge-incomplete',
        'overtime': 'badge-overtime',
    }
    return colors.get(status, 'badge-draft')
