from functools import lru_cache

from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin  # Используем Unfold ModelAdmin
from trucks.models import Route, Truck
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Route)
class RouteAdmin(ModelAdmin):  # Используем Unfold ModelAdmin
    list_display = ('truck', 'unique_number', 'view_orders_button', 'display_status', 'created_at',)
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

    @admin.display(description="Статус")
    def display_status(self, instance):
        # Кэшируем выборку статусов для оптимизации
        @lru_cache
        def get_status_dict():
            return dict(Route.STATUS_CHOICES)

        # Стандартные стили
        base_style = "display: flex; align-items: center; justify-content: left; padding: 6px 6px; padding-left: 10px; " \
                     "border-radius: 6px; font-size: 14px; font-weight: 500; gap: 6px;"
        icon_base_style = "font-size: 18px; vertical-align: middle;"

        # Определяем стили и иконки для статусов
        status_styles = {
            'loading': ("#f8c471; color: black;", "hourglass_top"),
            'on_way': ("#6fbf73; color: white;", "local_shipping"),
            'unloading': ("#b0a8b9; color: black;", "unarchive"),
            'completed': ("#88d0a0; color: black;", "check_circle"),
            'inactive': ("#bf616a; color: white;", "cancel"),
        }

        # Получаем стиль и иконку
        style, icon = status_styles.get(instance.status, ("#d1d5db; color: black;", ""))
        status_display = get_status_dict().get(instance.status, instance.status)

        # Генерируем HTML
        icon_html = f'<span class="material-symbols-outlined" style="{icon_base_style}">{icon}</span>' if icon else ""
        return mark_safe(
            f'''<div style="{base_style} background-color: {style}">
                    {icon_html}
                    <span>{status_display}</span>
                </div>'''
        )


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
