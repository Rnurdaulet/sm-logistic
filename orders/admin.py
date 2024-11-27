from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'status', 'sender', 'receiver', 'price', 'paid_amount', 'is_cashless', 'date')
    list_filter = ('status', 'is_cashless', 'date')
    search_fields = (
        'order_number',
        'sender__full_name',
        'receiver__full_name',
    )
    autocomplete_fields = ('sender', 'receiver', 'shelf')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'date', 'add_full_payment_button')
    fieldsets = (
        ("Основная информация", {
            'fields': ('order_number', 'status', 'sender', 'receiver', 'seat_count', 'comment', 'image',)
        }),
        ("Финансовые данные", {
            'fields': ('is_cashless', 'price', 'paid_amount', 'add_full_payment_button')
        }),
        ("Склад", {
            'fields': ('shelf',)
        }),
        ("Дополнительно", {
            'fields': ('date', 'created_at', 'updated_at')
        })
    )

    def add_full_payment_button(self, obj):
        # Добавляем кнопку с JS
        return mark_safe("""
            <button type="button" class="button" style="margin-top: 10px; padding: 10px;" onclick="setFullPayment()">Оплата полностью</button>
            <script>
                function setFullPayment() {{
                    const priceField = document.getElementById('id_price');
                    const paidAmountField = document.getElementById('id_paid_amount');
                    if (priceField && paidAmountField) {{
                        paidAmountField.value = priceField.value;
                    }}
                }}
            </script>
        """)

    add_full_payment_button.short_description = "Оплата полностью"

