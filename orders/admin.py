from django.urls import path
from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import Order
from orders.services import get_filtered_orders_url, redirect_with_custom_title


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'status', 'sender', 'receiver', 'price', 'paid_amount', 'shelf')
    list_filter = ('status', 'is_cashless', 'date', 'shelf', 'shelf__sector__area__warehouse')
    search_fields = (
        'order_number',
        'sender__full_name',
        'sender__phone_numbers__number',
        'receiver__full_name',
        'receiver__phone_numbers__number',
    )
    autocomplete_fields = ('sender', 'receiver', 'shelf', 'route')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'date', 'add_full_payment_button')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('by-route/<int:route_id>/', self.admin_site.admin_view(self.filtered_orders_by_route), name='orders_by_route'),
            path('by-warehouse/<int:warehouse_id>/', self.admin_site.admin_view(self.filtered_orders_by_warehouse), name='orders_by_warehouse'),
            path('by-area/<int:area_id>/', self.admin_site.admin_view(self.filtered_orders_by_area), name='orders_by_area'),
            path('by-sector/<int:sector_id>/', self.admin_site.admin_view(self.filtered_orders_by_sector), name='orders_by_sector'),
            path('by-shelf/<int:shelf_id>/', self.admin_site.admin_view(self.filtered_orders_by_shelf), name='orders_by_shelf'),
        ]
        return custom_urls + urls

    def filtered_orders_by_route(self, request, route_id):
        from trucks.models import Route
        route = Route.objects.get(pk=route_id)
        url, title = get_filtered_orders_url(route, "route", "admin:orders_order_changelist", "Заказы для маршрута")
        return redirect_with_custom_title(request, url, title)

    def filtered_orders_by_warehouse(self, request, warehouse_id):
        from warehouse.models import Warehouse
        warehouse = Warehouse.objects.get(pk=warehouse_id)
        url, title = get_filtered_orders_url(warehouse, "shelf__sector__area__warehouse", "admin:orders_order_changelist", "Заказы для склада")
        return redirect_with_custom_title(request, url, title)

    def filtered_orders_by_area(self, request, area_id):
        from warehouse.models import Area
        area = Area.objects.get(pk=area_id)
        url, title = get_filtered_orders_url(area, "shelf__sector__area", "admin:orders_order_changelist", "Заказы для области")
        return redirect_with_custom_title(request, url, title)

    def filtered_orders_by_sector(self, request, sector_id):
        from warehouse.models import Sector
        sector = Sector.objects.get(pk=sector_id)
        url, title = get_filtered_orders_url(sector, "shelf__sector", "admin:orders_order_changelist", "Заказы для сектора")
        return redirect_with_custom_title(request, url, title)

    def filtered_orders_by_shelf(self, request, shelf_id):
        from warehouse.models import Shelf
        shelf = Shelf.objects.get(pk=shelf_id)
        url, title = get_filtered_orders_url(shelf, "shelf", "admin:orders_order_changelist", "Заказы для полки")
        return redirect_with_custom_title(request, url, title)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = request.session.pop('custom_title', 'Список заказов')
        return super().changelist_view(request, extra_context=extra_context)

    def add_full_payment_button(self, obj):
        """
        Кнопка для установки полной оплаты.
        """
        return mark_safe("""
            <button type="button" class="button" style="margin-top: 10px; padding: 10px;" onclick="setFullPayment()">Оплата полностью</button>
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
