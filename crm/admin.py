from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Client, PhoneNumber


class PhoneNumberInline(TabularInline):  # Используем Unfold TabularInline
    model = PhoneNumber
    extra = 0
    min_num = 1
    fields = ['number']
    verbose_name = "Номер телефона"
    verbose_name_plural = "Номера телефонов"


@admin.register(Client)
class ClientAdmin(ModelAdmin):  # Используем Unfold ModelAdmin
    list_display = ['full_name', 'get_phone_numbers', 'created_at', 'updated_at']
    search_fields = ['full_name', 'phone_numbers__number']  # Поиск по имени и номеру телефона
    inlines = [PhoneNumberInline]
    ordering = ['-created_at']
    list_filter = ['created_at', 'updated_at']  # Фильтрация по дате
    readonly_fields = ['created_at', 'updated_at']  # Поля только для чтения
    form_layout = [  # Макет формы
        ('Основная информация', {
            'fields': ['full_name', 'created_at', 'updated_at']
        }),
    ]
    compressed_fields = True  # Сжатый режим полей (по умолчанию False)
    warn_unsaved_form = True  # Предупреждение об изменениях
    actions_on_top = True  # Показывать действия на верхней панели
    actions_on_bottom = True  # Отключить действия на нижней панели

    def get_phone_numbers(self, obj):
        """Форматированный вывод номеров телефонов."""
        return ", ".join([phone.number for phone in obj.phone_numbers.all()])
    get_phone_numbers.short_description = "Номера телефонов"


@admin.register(PhoneNumber)
class PhoneNumberAdmin(ModelAdmin):  # Используем Unfold ModelAdmin
    list_display = ['number', 'client']
    search_fields = ['number', 'client__full_name']
    ordering = ['number']
    list_filter = ['client']  # Фильтрация по клиенту
    form_layout = [  # Макет формы
        ('Детали номера', {
            'fields': ['number', 'client']
        }),
    ]
    compressed_fields = False  # Сжатый режим полей
    warn_unsaved_form = True  # Предупреждение об изменениях
