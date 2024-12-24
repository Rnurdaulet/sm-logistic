from django.db import models
from crm.models import Client
from services.order_image_service import OrderImageService
from services.qr_code_service import QRCodeService
from services.unique_number_service import UniqueNumberService
from trucks.models import Route
from warehouse.models import Shelf
from simple_history.models import HistoricalRecords


class Order(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Принят'),
        ('loading', 'Погрузка'),
        ('in_transit', 'В пути'),
        ('unloading', 'Выгрузка'),
        ('in_warehouse', 'На складе'),
        ('completed', 'Выдан'),
        ('canceled', 'Отменён'),
        ('return', 'Возврат'),
    ]

    order_number = models.CharField("Номер заказа", max_length=20, unique=True, editable=False)
    status = models.CharField(
        "Статус заказа",
        max_length=20,
        choices=STATUS_CHOICES,
        default='accepted'
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
    qr_code = models.ImageField("QR-код", upload_to="orders/qr_codes/", blank=True, null=True)
    date = models.DateTimeField("Дата", auto_now_add=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        """
        Сохраняет объект, оптимизирует изображение и генерирует номер заказа и QR-код.
        """
        is_new = self.pk is None

        # Первичное сохранение нового объекта для получения `pk`
        if is_new:
            super().save(*args, **kwargs)

        # Генерация номера заказа
        if not self.order_number:
            self.order_number = UniqueNumberService.generate_unique_number(Order)
            super().save(update_fields=["order_number"])

        # Генерация и сохранение QR-кода
        if not self.qr_code:
            QRCodeService.generate_qr_code(
                instance=self,
                qr_data=f"O{self.order_number}",
                text_parts=[
                    f"{self.order_number}",
                    f"О:{self.sender.get_first_phone_number()}",
                    f"П:{self.receiver.get_first_phone_number()}"
                ],
                file_prefix="O"
            )
            super().save(update_fields=["qr_code"])  # Обновляем только qr_code

        # Оптимизация изображения перед сохранением
        if self.image:
            optimized_image = OrderImageService.optimize_image(self.image)
            self.image.save(self.image.name, optimized_image, save=False)

        # Если статус изменяется на 'completed', убираем заказ с полки
        if self.status == 'completed' and self.shelf is not None:
            self.shelf = None
        # Если объект не новый, сохраняем изменения как обычно
        if not is_new:
            super().save(*args, **kwargs)


    def __str__(self):
        return f"№{self.order_number} от {self.sender} к {self.receiver} на {self.price}₸"
