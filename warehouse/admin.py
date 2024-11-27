from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import Warehouse, Area, Sector, Shelf
from orders.models import Order


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'view_orders_button')
    search_fields = ('name', 'location')
    ordering = ('name',)

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра заказов, связанных с данным складом через Shelves.
        """
        orders_count = Order.objects.filter(shelf__sector__area__warehouse=obj).count()
        if orders_count > 0:
            url = reverse('admin:orders_by_warehouse', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы склада ({})</a>',
                url,
                orders_count
            )
        return ""

    view_orders_button.short_description = "Заказы"


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'view_orders_button')
    search_fields = ('name', 'warehouse__name')
    list_filter = ('warehouse',)
    autocomplete_fields = ('warehouse',)
    ordering = ('name',)

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра заказов, связанных с данной областью через Shelves.
        """
        orders_count = Order.objects.filter(shelf__sector__area=obj).count()
        if orders_count > 0:
            url = reverse('admin:orders_by_area', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы области ({})</a>',
                url,
                orders_count
            )
        return ""

    view_orders_button.short_description = "Заказы"


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'view_orders_button')
    search_fields = ('name', 'area__name', 'area__warehouse__name')
    list_filter = ('area__warehouse', 'area')
    autocomplete_fields = ('area',)
    ordering = ('name',)

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра заказов, связанных с данным сектором через Shelves.
        """
        orders_count = Order.objects.filter(shelf__sector=obj).count()
        if orders_count > 0:
            url = reverse('admin:orders_by_sector', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы сектора ({})</a>',
                url,
                orders_count
            )
        return ""

    view_orders_button.short_description = "Заказы"


@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ('name', 'surface', 'sector', 'view_orders_button')
    search_fields = ('name', 'sector__name', 'sector__area__name', 'sector__area__warehouse__name')
    list_filter = ('surface', 'sector__area__warehouse', 'sector__area')
    autocomplete_fields = ('sector',)
    ordering = ('name',)

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра заказов, связанных с данной полкой.
        """
        orders_count = Order.objects.filter(shelf=obj).count()
        if orders_count > 0:
            url = reverse('admin:orders_by_shelf', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы полки ({})</a>',
                url,
                orders_count
            )
        return ""

    view_orders_button.short_description = "Заказы"
