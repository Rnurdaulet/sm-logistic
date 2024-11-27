from django.contrib import admin
from .models import Client, PhoneNumber


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1
    min_num = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'get_phone_numbers', 'created_at', 'updated_at')
    search_fields = ('full_name', 'phone_numbers__number')  # Поиск по имени и номеру телефона
    inlines = [PhoneNumberInline]
    ordering = ('-created_at',)


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'client')
    search_fields = ('number', 'client__full_name')
    ordering = ('number',)
