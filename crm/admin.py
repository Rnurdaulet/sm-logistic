from django.contrib import admin
from .models import Client, PhoneNumber

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1  # Количество пустых строк для добавления
    verbose_name = "Номер телефона"
    verbose_name_plural = "Номера телефонов"

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_numbers', 'created_at', 'updated_at')  # Поля, отображаемые в списке
    search_fields = ('full_name', 'phone_numbers__number')  # Поиск по ФИО и номерам телефонов
    list_filter = ('created_at', 'updated_at')  # Фильтры по дате
    inlines = [PhoneNumberInline]  # Включение номеров телефонов в клиентскую форму

    def phone_numbers(self, obj):
        """Возвращает все номера телефонов клиента."""
        return ", ".join([phone.number for phone in obj.phone_numbers.all()])
    phone_numbers.short_description = "Номера телефонов"

