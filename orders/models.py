from django.db import models
from django.utils import timezone
from image_optimizer.fields import OptimizedImageField

from crm.models import Client
from trucks.models import Route
from warehouse.models import Shelf
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from pathlib import Path


class Order(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Принят'),
        ('loading', 'Погрузка'),
        ('in_transit', 'В пути'),
        ('unloading', 'Выгрузка'),
        ('in_warehouse', 'На складе'),
        ('completed', 'Выдан'),
        ('canceled', 'Отменён'),
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
    # image = OptimizedImageField(
    #     upload_to='orders/photos/',
    #     optimized_image_output_size=1024,  # Опционально: размер вывода
    #     optimized_image_resize_method='thumbnail',  # Опционально: метод изменения размера
    #     blank=True, null=True
    # )

    date = models.DateTimeField("Дата", auto_now_add=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        """
        Сохраняет объект и оптимизирует изображение пропорционально без белых полей.
        """
        is_new = self.pk is None

        # Сохраняем объект для получения `pk`
        if is_new:
            super().save(*args, **kwargs)

        # Оптимизация изображения
        if self.image:
            self.optimize_image()

        # Генерация номера заказа
        if not self.order_number:
            unique_id = str(self.id).zfill(4)
            creation_date = self.created_at or timezone.now()
            self.created_at = creation_date  # Устанавливаем дату создания, если не задана
            self.order_number = f"{creation_date.strftime('%d%m')}-{unique_id}"
            super().save(update_fields=['order_number'])

        # Если объект уже существующий, сохраняем его как обычно
        if not is_new:
            super().save(*args, **kwargs)

    def optimize_image(self):
        """
        Масштабирует изображение пропорционально без белых полей.
        """
        try:
            img = Image.open(self.image)
            img = img.convert('RGB')  # Конвертируем в RGB для совместимости

            max_width, max_height = 1024, 1024
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)  # Используем LANCZOS вместо ANTIALIAS

            # Сохраняем оптимизированное изображение в памяти
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)

            # Обновляем файл изображения
            self.image.save(self.image.name, ContentFile(buffer.read()), save=False)
            buffer.close()

        except Exception as e:
            raise ValueError(f"Ошибка оптимизации изображения: {e}")

    def __str__(self):
        return f"Заказ №{self.order_number} от {self.sender} к {self.receiver} на {self.price}₸"
