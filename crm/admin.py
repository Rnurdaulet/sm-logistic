from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Client, PhoneNumber


class PhoneNumberInline(TabularInline):
    model = PhoneNumber
    extra = 0
    fields = ['number']
    verbose_name = "Номер телефона"
    verbose_name_plural = "Номера телефонов"


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ['full_name', 'get_phone_numbers', 'created_at', 'updated_at']
    search_fields = ['full_name', 'phone_numbers__number']
    inlines = [PhoneNumberInline]
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    form_layout = [
        ('Основная информация', {'fields': ['full_name', 'created_at', 'updated_at']}),
    ]
    compressed_fields = True
    warn_unsaved_form = True
    actions_on_top = True
    actions_on_bottom = False

    def get_phone_numbers(self, obj):
        return obj.get_phone_numbers()
    get_phone_numbers.short_description = "Номера телефонов"


@admin.register(PhoneNumber)
class PhoneNumberAdmin(ModelAdmin):
    list_display = ['number', 'client']
    search_fields = ['number', 'client__full_name']
    ordering = ['number']
    list_filter = ['client']
    form_layout = [
        ('Детали номера', {'fields': ['number', 'client']}),
    ]
    compressed_fields = False
    warn_unsaved_form = True
