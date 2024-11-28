from django.contrib import admin
from django.urls import path
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter

from .models import Order, OrderStatus
from orders.services import get_filtered_orders_url, redirect_with_custom_title


# Вспомогательные функции для фильтрации
def get_filtered_orders(request, model_cls, field, model_id, title_prefix, admin_url):
    obj = model_cls.objects.get(pk=model_id)
    url, title = get_filtered_orders_url(obj, field, admin_url, f"{title_prefix} для {obj}")
    return redirect_with_custom_title(request, url, title)


# Custom view-функции для фильтрации
def filtered_orders_by_route(request, route_id):
    from trucks.models import Route
    return get_filtered_orders(request, Route, "route", route_id, "Заказы", "admin:orders_order_changelist")


def filtered_orders_by_warehouse(request, warehouse_id):
    from warehouse.models import Warehouse
    return get_filtered_orders(request, Warehouse, "shelf__sector__area__warehouse", warehouse_id, "Заказы",
                               "admin:orders_order_changelist")


def filtered_orders_by_area(request, area_id):
    from warehouse.models import Area
    return get_filtered_orders(request, Area, "shelf__sector__area", area_id, "Заказы", "admin:orders_order_changelist")


def filtered_orders_by_sector(request, sector_id):
    from warehouse.models import Sector
    return get_filtered_orders(request, Sector, "shelf__sector", sector_id, "Заказы", "admin:orders_order_changelist")


def filtered_orders_by_shelf(request, shelf_id):
    from warehouse.models import Shelf
    return get_filtered_orders(request, Shelf, "shelf", shelf_id, "Заказы", "admin:orders_order_changelist")


# Админка OrderAdmin
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    """
    Админка для модели заказов с кастомными действиями и фильтрацией.
    """
    list_display = ('order_number', 'status', 'sender', 'receiver', 'price', 'paid_amount', 'shelf')
    list_filter = (("status", RelatedDropdownFilter), 'is_cashless', 'date', 'shelf', 'shelf__sector__area__warehouse')
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
        return mark_safe("""
            <button type="button" class="bg-primary-600 block border border-transparent font-medium px-3 py-2 rounded-md text-white w-full lg:w-auto" style="margin-top: 10px; padding: 10px;" onclick="setFullPayment()">Оплата полностью</button>
            <script>
                function setFullPayment() {
                    const priceField = document.getElementById('id_price');
                    const paidAmountField = document.getElementById('id_paid_amount');
                    if (priceField && paidAmountField) {
                        paidAmountField.value = priceField.value;
                    }
                }
            </script>
        """)

    add_full_payment_button.short_description = "Оплата полностью"


@admin.register(OrderStatus)
class OrderStatusAdmin(ModelAdmin):
    """
    Админка для модели статусов заказа.
    """
    list_display = ('name', 'description')  # Отображаемые поля в списке
    search_fields = ('name', 'description')  # Поиск по имени и описанию
    ordering = ('name',)  # Сортировка по имени
    list_filter = ('name',)  # Фильтр по имени
