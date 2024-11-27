from django.db import models
from crm.models import Client


class OrderStatus(models.Model):
    name = models.CharField("Название статуса", max_length=50, unique=True)
    description = models.TextField("Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return self.name


class Order(models.Model):
    seat_count = models.PositiveIntegerField("Количество мест")
    comment = models.TextField("Комментарий", blank=True, null=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    is_cashless = models.BooleanField("Безналичный расчёт", default=False)
    paid_amount = models.DecimalField("Оплачено", max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField("Дата", auto_now_add=True)
    sender = models.ForeignKey(Client, related_name="sent_orders", on_delete=models.CASCADE, verbose_name="Отправитель")
    receiver = models.ForeignKey(Client, related_name="received_orders", on_delete=models.CASCADE,
                                 verbose_name="Получатель")
    image = models.ImageField("Фото", upload_to="orders/photos/", blank=True, null=True)
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.PROTECT,
        verbose_name="Статус заказа",
        null=False,
        blank=False
    )
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date']

    def __str__(self):
        return f"Заказ от {self.sender} к {self.receiver} на {self.price}₸"
