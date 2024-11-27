from django.contrib import admin
from trucks.models import Route
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('truck', 'unique_number', 'status', 'created_at', 'view_orders_button')
    list_filter = ('status', 'created_at', 'truck')
    search_fields = ('truck__name', 'unique_number')

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра кастомной страницы заказов для маршрута.
        Отображается только если есть заказы.
        """
        orders_count = obj.orders.count()  # Подсчёт связанных заказов
        if orders_count > 0:
            url = reverse('admin:orders_by_route', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы маршрута ({})</a>',
                url,
                orders_count
            )
        return ""  # Возвращаем пустую строку, если заказов нет

    view_orders_button.short_description = "Заказы"  # Заголовок колонки
