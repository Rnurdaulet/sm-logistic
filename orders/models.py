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
import segno
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
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

        # Оптимизация изображения
        if self.image:
            self.optimize_image()

        # Генерация номера заказа
        if not self.order_number:
            creation_date = self.created_at or timezone.now()
            self.created_at = creation_date  # Устанавливаем дату создания, если не задана

            # Получаем ID последнего заказа за текущий день
            start_of_day = creation_date.date()
            unique_id = (
                    Order.objects.filter(created_at__date=start_of_day)
                    .aggregate(max_id=models.Max("id"))["max_id"] or 0
            )

            # Формируем номер заказа
            self.order_number = f"{creation_date.strftime('%d%m%y')}-{unique_id + 1:04d}"

            # Сохраняем только поле order_number
            super().save(update_fields=["order_number"])

        # Генерация и сохранение QR-кода
        if not self.qr_code:
            self.generate_and_save_qr_code()
            super().save(update_fields=["qr_code"])  # Сохраняем только QR-код

        # Если объект не новый, сохраняем изменения как обычно
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

    def generate_and_save_qr_code(self):
        # Генерация QR-кода
        qr = segno.make(f"O{self.order_number}", micro=False)
        buffer = BytesIO()
        qr.save(buffer, kind='png', scale=5)
        buffer.seek(0)

        # Открываем QR-код как изображение
        qr_image = Image.open(buffer)

        # Создаём текст цепочки с разделением на строки
        text_parts = [
            f"{self.order_number}",
            f"О:{self.sender.get_first_phone_number()}",
            f"П:{self.receiver.get_first_phone_number()}"
        ]

        # Настраиваем шрифт
        try:
            font = ImageFont.truetype("arial.ttf", size=20)
        except IOError:
            font = ImageFont.load_default()

        # Определяем ширину и высоту текста
        draw = ImageDraw.Draw(qr_image)
        text_width = max(int(draw.textbbox((0, 0), line, font=font)[2]) for line in text_parts)
        text_height = sum(int(draw.textbbox((0, 0), line, font=font)[3]) for line in text_parts) + (
                len(text_parts) - 1) * 5

        # Создаем новое изображение, добавляя место справа для текста
        new_width = qr_image.width + text_width + 20
        new_height = max(qr_image.height, text_height)
        new_image = Image.new("RGB", (new_width, new_height), "white")
        new_image.paste(qr_image, (0, 0))

        # Рисуем текст справа
        text_x = qr_image.width + 10
        current_y = (new_height - text_height) // 2
        draw = ImageDraw.Draw(new_image)
        for line in text_parts:
            draw.text((text_x, current_y), line, fill="black", font=font)
            current_y += int(draw.textbbox((0, 0), line, font=font)[3]) + 5

        # Сохранение изображения
        buffer = BytesIO()
        new_image.save(buffer, format="PNG")
        buffer.seek(0)

        # Сохраняем изображение в поле qr_code
        file_name = f"{self.order_number}_qr.png"
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return f"№{self.order_number} от {self.sender} к {self.receiver} на {self.price}₸"
