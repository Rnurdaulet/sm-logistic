from django import template
from orders.models import Order

register = template.Library()

@register.filter
def get_status_display(value):
    return dict(Order.STATUS_CHOICES).get(value, value)
