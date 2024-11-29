from django.db import models
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
    receiver = models.ForeignKey(Client, related_name="received_orders", on_delete=models.CASCADE, verbose_name="Получатель")
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
        """
        Сохраняет объект, генерирует номер заказа и оптимизирует изображение.
        """
        # Генерация номера заказа, если его нет
        if not self.order_number:
            unique_id = str(self.id).zfill(4) if self.id else '0001'
            self.order_number = f"{self.created_at.strftime('%d%m')}-{unique_id}"

        super().save(*args, **kwargs)

        # Оптимизация изображения, если загружено
        if self.image:
            self.optimize_image()

    def optimize_image(self):
        """
        Уменьшает размер изображения и удаляет лишние метаданные.
        """
        try:
            img = Image.open(self.image)
            img = img.copy()
            image_format = img.format or 'JPEG'
            valid_formats = ['JPEG', 'PNG', 'WEBP']
            if image_format not in valid_formats:
                raise ValueError(f"Unsupported image format: {image_format}")
            max_width = 720
            if img.width > max_width:
                new_height = int((max_width / img.width) * img.height)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            save_params = {"format": image_format, "optimize": True}
            if image_format == "JPEG":
                save_params["quality"] = 85
            img.save(buffer, **save_params)
            buffer.seek(0)
            original_file_path = Path(self.image.path)
            self.image.save(self.image.name, ContentFile(buffer.read()), save=False)
            if original_file_path.exists():
                original_file_path.unlink()
        except Exception as e:
            raise ValueError(f"Error optimizing image: {e}")

    def __str__(self):
        return f"Заказ №{self.order_number} от {self.sender} к {self.receiver} на {self.price}₸"
