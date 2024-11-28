from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, render
from unfold.admin import ModelAdmin
from .models import Warehouse, Area, Sector, Shelf
from orders.models import Order


class OrderButtonMixin:
    """
    Миксин для добавления кнопки просмотра заказов в админке.
    """
    def get_orders_count(self, queryset):
        raise NotImplementedError("Метод должен быть реализован в классе-наследнике.")

    def view_orders_button(self, obj):
        orders_count = self.get_orders_count(obj)
        if orders_count > 0:
            url = reverse(self.orders_url_name, args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы ({})</a>',
                url,
                orders_count
            )
        return format_html('<span style="color: gray;">Нет заказов</span>')

    view_orders_button.short_description = "Заказы"


@admin.register(Warehouse)
class WarehouseAdmin(OrderButtonMixin, ModelAdmin):
    list_display = ('name', 'location', 'view_orders_button')
    search_fields = ('name', 'location')
    ordering = ('name',)
    orders_url_name = 'admin:orders_by_warehouse'

    def get_orders_count(self, obj):
        return Order.objects.filter(shelf__sector__area__warehouse=obj).count()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'orders/<int:warehouse_id>/',
                self.admin_site.admin_view(self.view_orders),
                name=self.orders_url_name
            ),
        ]
        return custom_urls + urls

    def view_orders(self, request, warehouse_id):
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        orders = Order.objects.filter(shelf__sector__area__warehouse=warehouse)
        context = dict(
            self.admin_site.each_context(request),
            warehouse=warehouse,
            orders=orders
        )
        return render(request, "admin/orders_by_warehouse.html", context)

@admin.register(Area)
class AreaAdmin(OrderButtonMixin, ModelAdmin):
    list_display = ('name', 'warehouse', 'view_orders_button')
    search_fields = ('name', 'warehouse__name')  # Поиск по названию области и склада
    list_filter = ('warehouse',)  # Фильтрация по складу
    autocomplete_fields = ('warehouse',)
    ordering = ('name',)
    orders_url_name = 'admin:orders_by_area'

    def get_orders_count(self, obj):
        return Order.objects.filter(shelf__sector__area=obj).count()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'orders/<int:area_id>/',
                self.admin_site.admin_view(self.view_orders),
                name=self.orders_url_name
            ),
        ]
        return custom_urls + urls

    def view_orders(self, request, area_id):
        area = get_object_or_404(Area, id=area_id)
        orders = Order.objects.filter(shelf__sector__area=area)
        context = dict(
            self.admin_site.each_context(request),
            area=area,
            orders=orders
        )
        return render(request, "admin/orders_by_area.html", context)


@admin.register(Sector)
class SectorAdmin(OrderButtonMixin, ModelAdmin):
    list_display = ('name', 'area', 'view_orders_button')
    search_fields = ('name', 'area__name', 'area__warehouse__name')  # Поиск по секторам, областям и складам
    list_filter = ('area__warehouse', 'area')  # Фильтрация по складу и области
    autocomplete_fields = ('area',)
    ordering = ('name',)
    orders_url_name = 'admin:orders_by_sector'

    def get_orders_count(self, obj):
        return Order.objects.filter(shelf__sector=obj).count()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'orders/<int:sector_id>/',
                self.admin_site.admin_view(self.view_orders),
                name=self.orders_url_name
            ),
        ]
        return custom_urls + urls

    def view_orders(self, request, sector_id):
        sector = get_object_or_404(Sector, id=sector_id)
        orders = Order.objects.filter(shelf__sector=sector)
        context = dict(
            self.admin_site.each_context(request),
            sector=sector,
            orders=orders
        )
        return render(request, "admin/orders_by_sector.html", context)

@admin.register(Shelf)
class ShelfAdmin(OrderButtonMixin, ModelAdmin):
    list_display = ('name', 'surface', 'sector', 'view_orders_button')
    search_fields = ('name', 'sector__name', 'sector__area__name', 'sector__area__warehouse__name')
    list_filter = ('surface', 'sector__area__warehouse', 'sector__area')
    autocomplete_fields = ('sector',)
    ordering = ('name',)
    orders_url_name = 'admin:orders_by_shelf'

    def get_orders_count(self, obj):
        return Order.objects.filter(shelf=obj).count()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'orders/<int:shelf_id>/',
                self.admin_site.admin_view(self.view_orders),
                name=self.orders_url_name
            ),
        ]
        return custom_urls + urls

    def view_orders(self, request, shelf_id):
        shelf = get_object_or_404(Shelf, id=shelf_id)
        orders = Order.objects.filter(shelf=shelf)
        context = dict(
            self.admin_site.each_context(request),
            shelf=shelf,
            orders=orders
        )
        return render(request, "admin/orders_by_shelf.html", context)
