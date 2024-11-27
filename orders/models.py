import uuid
from io import BytesIO
from django.db import models
from crm.models import Client
from trucks.models import Route
from warehouse.models import Shelf
from PIL import Image
from django.core.files.base import ContentFile


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

        # Обработка изображения
        if self.image:
            self.optimize_image()

    def optimize_image(self):
        from pathlib import Path  # Для безопасной работы с путями

        # Открываем изображение
        img = Image.open(self.image)

        # Удаляем метаданные
        img = img.copy()

        # Получаем текущий формат изображения
        image_format = img.format or 'JPEG'
        valid_formats = ['JPEG', 'PNG', 'WEBP']
        if image_format not in valid_formats:
            raise ValueError(f"Unsupported image format: {image_format}")

        # Меняем размер до ширины 720px с сохранением пропорций
        max_width = 720
        if img.width > max_width:
            new_height = int((max_width / img.width) * img.height)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Подготовка к оптимизации
        buffer = BytesIO()
        save_params = {"format": image_format, "optimize": True}
        if image_format == "JPEG":
            save_params["quality"] = 85  # Устанавливаем качество для JPEG

        # Сохраняем изображение в памяти
        img.save(buffer, **save_params)
        buffer.seek(0)

        # Сохраняем имя оригинального файла для удаления
        original_file_path = Path(self.image.path)

        # Перезаписываем файл изображения
        self.image.save(self.image.name, ContentFile(buffer.read()), save=False)

        # Удаляем оригинальный файл
        if original_file_path.exists():
            original_file_path.unlink()

    def __str__(self):
        return f"Заказ №{self.order_number} от {self.sender} к {self.receiver} на {self.price}₸"
