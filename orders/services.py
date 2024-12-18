from django.db import transaction
from warehouse.models import Shelf
from orders.models import Order

class OrderShelfService:
    @staticmethod
    @transaction.atomic
    def add_orders_to_shelf(order_numbers: list, shelf_unique_id: str):
        """
        Добавляет все заказы с указанными номерами заказов на полку с заданным уникальным идентификатором.

        :param order_numbers: Список номеров заказов
        :param shelf_unique_id: Уникальный идентификатор полки
        :raises ValueError: Если полка не найдена или заказы отсутствуют
        """
        if not order_numbers:
            raise ValueError("Список номеров заказов пуст.")

        try:
            # Получаем полку по уникальному идентификатору
            shelf = Shelf.objects.get(unique_id=shelf_unique_id)
        except Shelf.DoesNotExist:
            raise ValueError(f"Полка с уникальным идентификатором {shelf_unique_id} не найдена.")

        # Получаем заказы с указанными номерами
        orders = Order.objects.filter(order_number__in=order_numbers)

        if not orders.exists():
            raise ValueError(f"Заказы с номерами {order_numbers} не найдены.")

        # Обновляем поле `shelf` у всех выбранных заказов
        orders.update(shelf=shelf)

        return f"Заказы с номерами {', '.join(order_numbers)} успешно добавлены на полку {shelf.unique_id}."
