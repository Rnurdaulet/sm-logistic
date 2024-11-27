import uuid
from django.db import models
from crm.models import Client
from trucks.models import Route
from warehouse.models import Shelf


class OrderStatus(models.Model):
    name = models.CharField("Название статуса", max_length=50, unique=True)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return self.name


class Order(models.Model):
    order_number = models.CharField("Номер заказа", max_length=20, unique=True, editable=False)
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.PROTECT,
        verbose_name="Статус заказа",
        null=False,
        blank=False
    )
    sender = models.ForeignKey(Client, related_name="sent_orders", on_delete=models.CASCADE, verbose_name="Отправитель")
    receiver = models.ForeignKey(Client, related_name="received_orders", on_delete=models.CASCADE,
                                 verbose_name="Получатель")
    shelf = models.ForeignKey(
        Shelf,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Полка",
        null=True,
        blank=True
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Маршрут",
        null=True,
        blank=True
    )
    seat_count = models.PositiveIntegerField("Количество мест")
    is_cashless = models.BooleanField("Безналичный расчёт", default=False)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField("Оплачено", max_digits=10, decimal_places=2)
    comment = models.TextField("Комментарий", blank=True, null=True)
    image = models.ImageField("Фото", upload_to="orders/photos/", blank=True, null=True)
    date = models.DateTimeField("Дата", auto_now_add=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сохраняем объект, чтобы получить ID

        if not self.order_number:
            # Генерация уникального номера заказа с использованием ID
            unique_id = str(self.id).zfill(4)  # Приводим ID к формату с 6 символами (например, 000001)
            self.order_number = f"{self.created_at.strftime('%d%m')}-{unique_id}"
            super().save(*args, **kwargs)  # Повторное сохранение с обновлённым номером заказа

    def __str__(self):
        return f"Заказ №{self.order_number} от {self.sender} к {self.receiver} на {self.price}₸"

