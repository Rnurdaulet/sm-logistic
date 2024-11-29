from django.contrib import admin
from django.urls import path
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter, RangeDateFilter

from .models import Order
from orders.services import get_filtered_orders_url, redirect_with_custom_title


# Вспомогательные функции для фильтрации
def get_filtered_orders(request, field, value, title_prefix, admin_url):
    url, title = get_filtered_orders_url(value, field, admin_url, f"{title_prefix} для {value}")
    return redirect_with_custom_title(request, url, title)


# Custom view-функции для фильтрации
def filtered_orders_by_route(request, route_id):
    return get_filtered_orders(request, "route_id", route_id, "Заказы", "admin:orders_order_changelist")


def filtered_orders_by_warehouse(request, warehouse_id):
    return get_filtered_orders(request, "shelf__sector__area__warehouse_id", warehouse_id, "Заказы",
                               "admin:orders_order_changelist")


def filtered_orders_by_area(request, area_id):
    return get_filtered_orders(request, "shelf__sector__area_id", area_id, "Заказы", "admin:orders_order_changelist")


def filtered_orders_by_sector(request, sector_id):
    return get_filtered_orders(request, "shelf__sector_id", sector_id, "Заказы", "admin:orders_order_changelist")


def filtered_orders_by_shelf(request, shelf_id):
    return get_filtered_orders(request, "shelf_id", shelf_id, "Заказы", "admin:orders_order_changelist")


# Админка OrderAdmin
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    """
    Админка для модели заказов с кастомными действиями и фильтрацией.
    """
    date_hierarchy = "date"
    list_display = ('order_number', 'get_status_display', 'sender', 'receiver', 'price', 'paid_amount', 'shelf')
    list_filter = (
        ("status", ChoicesDropdownFilter),
        'is_cashless',
        ("date", RangeDateFilter),
        ('shelf', RelatedDropdownFilter),
    )
    search_fields = (
        'order_number',
        'sender__full_name',
        'sender__phone_numbers__number',
        'receiver__full_name',
        'receiver__phone_numbers__number',
    )
    autocomplete_fields = ('sender', 'receiver', 'shelf', 'route')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'date', 'add_full_payment_button')

    fieldsets = (
        ("Основная информация", {
            'fields': ('order_number', 'status', 'sender', 'receiver', 'image', 'comment')
        }),
        ("Детали заказа", {
            'fields': ('seat_count', 'is_cashless', 'price', 'paid_amount', 'add_full_payment_button')
        }),
        ("Склад", {
            'fields': ('shelf',)
        }),
        ("Маршрут", {
            'fields': ('route',)
        }),
        ("Дополнительно", {
            'fields': ('date', 'created_at', 'updated_at',),
            'classes': ('collapse',),
            'description': "Заполните информацию о деталях заказа",
        }),
    )

    list_filter_submit = True
    list_filter_sheet = False
    list_fullwidth = True

    # Добавляем кастомные URL
    def get_urls(self):
        custom_urls = [
            path('by-route/<int:route_id>/', self.admin_site.admin_view(filtered_orders_by_route),
                 name='orders_by_route'),
            path('by-warehouse/<int:warehouse_id>/', self.admin_site.admin_view(filtered_orders_by_warehouse),
                 name='orders_by_warehouse'),
            path('by-area/<int:area_id>/', self.admin_site.admin_view(filtered_orders_by_area), name='orders_by_area'),
            path('by-sector/<int:sector_id>/', self.admin_site.admin_view(filtered_orders_by_sector),
                 name='orders_by_sector'),
            path('by-shelf/<int:shelf_id>/', self.admin_site.admin_view(filtered_orders_by_shelf),
                 name='orders_by_shelf'),
        ]
        return custom_urls + super().get_urls()

    # Кастомизация заголовка списка
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = request.session.pop('custom_title', 'Список заказов')
        return super().changelist_view(request, extra_context=extra_context)

    # Кнопка "Оплата полностью"
    def add_full_payment_button(self, obj):
        """
        Кнопка для установки полной оплаты.
        """
        return mark_safe(f"""
            <button type="button" class="bg-primary-600 block border border-transparent font-medium px-3 py-2 rounded-md text-white w-full lg:w-auto" style="margin-top: 10px; padding: 10px;" onclick="setFullPayment()">Оплата полностью</button>
            <script>
                function setFullPayment() {{
                    const priceField = document.getElementById('id_price');
                    const paidAmountField = document.getElementById('id_paid_amount');
                    if (priceField && paidAmountField) {{
                        paidAmountField.value = priceField.value;
                    }}
                }}
            </script>
        """)

    add_full_payment_button.short_description = "Оплата полностью"
