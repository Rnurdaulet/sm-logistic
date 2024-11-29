from django.apps import AppConfig

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = "Заказы"
