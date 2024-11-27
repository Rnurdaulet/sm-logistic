from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Client, PhoneNumber


class PhoneNumberInline(TabularInline):  # Используем Unfold TabularInline
    model = PhoneNumber
    extra = 0
    min_num = 1
    fields = ['number']  # Указываем, какие поля показывать


@admin.register(Client)
class ClientAdmin(ModelAdmin):  # Используем Unfold ModelAdmin
    list_display = ['full_name', 'get_phone_numbers', 'created_at', 'updated_at']
    search_fields = ['full_name', 'phone_numbers__number']  # Поиск по имени и номеру телефона
    inlines = [PhoneNumberInline]
    ordering = ['-created_at']
    form_layout = [  # Определяем макет формы для Unfold
        ('Основная информация', {
            'fields': ['full_name', 'created_at', 'updated_at']
        }),
    ]
    # Display fields in changeform in compressed mode
    compressed_fields = False  # Default: False

    # Warn before leaving unsaved changes in changeform
    warn_unsaved_form = True  # Default: False


@admin.register(PhoneNumber)
class PhoneNumberAdmin(ModelAdmin):  # Используем Unfold ModelAdmin
    list_display = ['number', 'client']
    search_fields = ['number', 'client__full_name']
    ordering = ['number']
    form_layout = [  # Определяем макет формы для Unfold
        ('Детали номера', {
            'fields': ['number', 'client']
        }),
    ]
