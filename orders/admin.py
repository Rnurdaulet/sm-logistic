from django.contrib import admin
from .models import Order, OrderStatus

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Поля, отображаемые в списке
    search_fields = ('name',)  # Поиск по названию статуса

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'status', 'seat_count', 'price', 'paid_amount', 'is_cashless', 'date')  # Поля для отображения
    list_filter = ('status', 'is_cashless', 'date')  # Фильтры по статусу, способу оплаты и дате
    search_fields = ('sender__full_name', 'receiver__full_name', 'status__name')  # Поиск по отправителю, получателю и статусу
    readonly_fields = ('date',)  # Поля, доступные только для чтения
    fieldsets = (
        (None, {
            'fields': ('sender', 'receiver', 'status', 'seat_count', 'comment', 'price', 'paid_amount', 'is_cashless')
        }),
        ('Дополнительно', {
            'fields': ('image', 'date'),
            'classes': ('collapse',)  # Скрытие дополнительного раздела
        }),
    )
    list_per_page = 25  # Количество записей на одной странице
    autocomplete_fields = ['sender', 'receiver']  # Для удобного выбора клиентов, если их много

    def get_queryset(self, request):
        """Оптимизация запросов для отображения списка заказов."""
        queryset = super().get_queryset(request)
        return queryset.select_related('sender', 'receiver', 'status')  # Предзагрузка связанных данных
