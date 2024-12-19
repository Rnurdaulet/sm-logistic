from import_export import fields
from import_export import resources
from django.utils.translation import gettext_lazy as _
from .models import Order


class OrderResource(resources.ModelResource):
    receiver_phone_numbers = fields.Field(column_name="Телефоны получателя")

    def dehydrate_receiver_phone_numbers(self, order):
        """
        Возвращает все номера телефона получателя через запятую.
        """
        if order.receiver:
            return order.receiver.get_phone_numbers()
        return "Нет номеров"


    def dehydrate_date(self, order):
        """
        Преобразует дату в формат %d.%m.%y.
        """
        return order.date.strftime('%d.%m.%y') if order.date else "Нет даты"

    status = fields.Field(column_name="Статус")

    def dehydrate_status(self, order):
        """
        Возвращает перевод статуса.
        """
        status_display = dict(Order.STATUS_CHOICES).get(order.status, "Неизвестный статус")
        return status_display

    is_cashless = fields.Field(column_name="Безналичный расчёт")

    def dehydrate_is_cashless(self, order):
        """
        Возвращает 'ДА' для True и 'НЕТ' для False.
        """
        return "ДА" if order.is_cashless else "НЕТ"

    order_number = fields.Field(attribute='order_number', column_name="Номер заказа")
    receiver_full_name = fields.Field(attribute='receiver__full_name', column_name="ФИО получателя")
    seat_count = fields.Field(attribute='seat_count', column_name="Количество мест")
    shelf_unique_id = fields.Field(attribute='shelf__unique_id', column_name="ID полки")
    price = fields.Field(attribute='price', column_name="Цена")
    truck_plate_number = fields.Field(attribute='route__truck__plate_number', column_name="Номер машины")
    date = fields.Field(attribute='date', column_name="Дата")

    class Meta:
        model = Order
        fields = (
            'order_number', 'status', 'receiver_full_name', 'receiver_phone_numbers',
            'seat_count', 'shelf_unique_id', 'price', 'is_cashless',
            'truck_plate_number', 'date',
        )
