from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline, TabularInline

from orders.models import Order
from .models import Warehouse, Area, Sector, Shelf


# Inline Classes
class ShelfInline(TabularInline):
    """Tabular Inline-дисплей для полок."""
    model = Shelf
    extra = 0
    fields = ("surface",)
    verbose_name = "Полка"
    verbose_name_plural = "Полки"


class SectorInline(StackedInline):
    """Stacked Inline-дисплей для секторов."""
    model = Sector
    extra = 0
    fields = ("name",)
    verbose_name = "Сектор"
    verbose_name_plural = "Секторы"


class AreaInline(StackedInline):
    """Stacked Inline-дисплей для областей."""
    model = Area
    extra = 0
    fields = ("name",)
    verbose_name = "Область"
    verbose_name_plural = "Области"


# Admin Classes
@admin.register(Warehouse)
class WarehouseAdmin(ModelAdmin):
    """Админка для модели склада с вложенными областями."""
    list_display = ("unique_id", "name", "location")
    search_fields = ("name", "location")
    ordering = ("name",)
    readonly_fields = ("unique_id",)
    inlines = [AreaInline]  # Только области на уровне склада


@admin.register(Area)
class AreaAdmin(ModelAdmin):
    """Админка для модели области с вложенными секторами."""
    list_display = ("unique_id", "name", "warehouse")
    search_fields = ("name", "warehouse__name")
    list_filter = ("warehouse",)
    ordering = ("warehouse__name", "name")
    readonly_fields = ("unique_id",)
    inlines = [SectorInline]  # Только сектора на уровне области


@admin.register(Sector)
class SectorAdmin(ModelAdmin):
    """Админка для модели сектора с вложенными полками."""
    list_display = ("unique_id", "name", "area", "get_warehouse", 'view_orders_button')
    search_fields = ("name", "area__name", "area__warehouse__name")
    list_filter = ("area__warehouse", "area")
    ordering = ("area__name", "name")
    readonly_fields = ("unique_id",)
    inlines = [ShelfInline]  # Только полки на уровне сектора

    def get_warehouse(self, obj):
        return obj.area.warehouse.name

    get_warehouse.short_description = "Склад"

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра заказов, связанных с сектором (через связанные полки).
        """
        # Подсчёт всех заказов, связанных с полками в текущем секторе
        orders_count = Order.objects.filter(shelf__sector=obj).count()
        if orders_count > 0:
            # Генерация ссылки на кастомный фильтр
            url = reverse('admin:orders_shelf__sector_id', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы ({})</a>',
                url,
                orders_count
            )
        # Если заказов нет
        return format_html('<span style="color: gray;">Нет заказов</span>')

    view_orders_button.short_description = "Заказы"


@admin.register(Shelf)
class ShelfAdmin(ModelAdmin):
    """Админка для модели полки."""
    list_display = ("unique_id", "surface", "sector", "sector_area", "sector_warehouse", 'view_orders_button')
    search_fields = ("unique_id", "sector__name", "sector__area__name", "sector__area__warehouse__name")
    list_filter = ("sector__area__warehouse", "sector__area", "surface")
    ordering = ("sector__name", "surface")
    readonly_fields = ("unique_id",)

    def sector_area(self, obj):
        return obj.sector.area.name

    sector_area.short_description = "Область"

    def sector_warehouse(self, obj):
        return obj.sector.area.warehouse.name

    sector_warehouse.short_description = "Склад"

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра заказов, связанных с маршрутом.
        """
        orders_count = Order.objects.filter(shelf_id=obj.id).count()
        if orders_count > 0:
            url = reverse('admin:orders_shelf_id', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы ({})</a>',
                url,
                orders_count
            )
        return format_html('<span style="color: gray;">Нет заказов</span>')

    view_orders_button.short_description = "Заказы"
