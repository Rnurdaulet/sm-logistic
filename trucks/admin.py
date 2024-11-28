from django.contrib import admin
from unfold.admin import ModelAdmin  # Используем Unfold ModelAdmin
from trucks.models import Route, Truck
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Route)
class RouteAdmin(ModelAdmin):  # Используем Unfold ModelAdmin
    list_display = ('truck', 'unique_number', 'status', 'created_at', 'updated_at', 'view_orders_button')
    list_filter = ('status', 'created_at', 'updated_at', 'truck')
    search_fields = ('truck__name', 'unique_number')
    ordering = ('-created_at',)  # Сортировка по умолчанию
    readonly_fields = ('created_at', 'updated_at', 'unique_number')  # Поля только для чтения
    form_layout = [  # Определяем макет формы для Unfold
        ('Основная информация', {
            'fields': ['truck', 'status', 'unique_number', 'created_at', 'updated_at']
        }),
    ]
    compressed_fields = True  # Сжатый режим полей
    warn_unsaved_form = True  # Предупреждение о несохранённых изменениях
    actions_on_top = True  # Действия на верхней панели
    actions_on_bottom = False  # Действия на нижней панели отключены

    def view_orders_button(self, obj):
        """
        Кнопка для просмотра кастомной страницы заказов для маршрута.
        Отображается только если есть заказы.
        """
        orders_count = getattr(obj, 'orders', []).count()  # Подсчёт связанных заказов
        if orders_count > 0:
            url = reverse('admin:orders_by_route', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Заказы маршрута ({})</a>',
                url,
                orders_count
            )
        return format_html('<span style="color: gray;">Нет заказов</span>')

    view_orders_button.short_description = "Заказы"  # Заголовок колонки


@admin.register(Truck)
class TruckAdmin(ModelAdmin):  # Добавляем админку для модели Truck
    list_display = ('name', 'plate_number')
    search_fields = ('name', 'plate_number')
    ordering = ('name',)  # Сортировка по имени
    form_layout = [  # Макет формы для Unfold
        ('Информация о фуре', {
            'fields': ['name', 'plate_number']
        }),
    ]
    compressed_fields = True  # Сжатый режим полей
