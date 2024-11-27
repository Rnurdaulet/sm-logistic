from django.contrib import admin
from .models import Order, OrderStatus


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'status', 'sender', 'receiver', 'price', 'paid_amount', 'is_cashless', 'date')
    list_filter = ('status', 'is_cashless', 'date')
    search_fields = (
        'order_number',
        'sender__full_name',  # Поиск по имени отправителя
        'sender__phone_numbers__number',  # Поиск по телефону отправителя
        'receiver__full_name',  # Поиск по имени получателя
        'receiver__phone_numbers__number',  # Поиск по телефону получателя
    )
    autocomplete_fields = ('sender', 'receiver', 'shelf')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'date')
    fieldsets = (
        ("Основная информация", {
            'fields': ('order_number', 'status', 'sender', 'receiver', 'shelf', 'seat_count', 'is_cashless')
        }),
        ("Финансовые данные", {
            'fields': ('price', 'paid_amount')
        }),
        ("Дополнительно", {
            'fields': ('comment', 'image', 'date', 'created_at', 'updated_at')
        }),
    )
    actions = ['mark_as_fully_paid']  # Регистрируем действие

    def mark_as_fully_paid(self, request, queryset):
        """
        Устанавливает paid_amount равным price для выбранных заказов.
        """
        updated_count = 0
        for order in queryset:
            if order.price > order.paid_amount:
                order.paid_amount = order.price
                order.save()
                updated_count += 1
        self.message_user(
            request,
            f"{updated_count} заказ(а/ов) был(и) обновлён(ы) как 'Оплачено полностью'."
        )

    mark_as_fully_paid.short_description = "Отметить как 'Оплачено полностью'"
