import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
import segno

from django.db import models

class Warehouse(models.Model):
    """Модель для представления склада."""
    name = models.CharField(max_length=255, verbose_name="Название склада")
    location = models.TextField(verbose_name="Местоположение", blank=True, null=True)
    unique_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        verbose_name="Уникальный ID",
    )

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        ordering = ["name"]  # Упорядочивание по имени

    def save(self, *args, **kwargs):
        # Проверка на уникальность ID только при создании объекта
        if not self.unique_id:
            max_id = Warehouse.objects.aggregate(max_id=models.Max("id"))["max_id"] or 0
            self.unique_id = f"{max_id + 1:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_id} - {self.name}"


class Area(models.Model):
    """Модель для представления области внутри склада."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="areas",
        verbose_name="Склад",
    )
    name = models.CharField(max_length=255, verbose_name="Название области")
    unique_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Уникальный ID",
    )

    class Meta:
        verbose_name = "Область"
        verbose_name_plural = "Области"
        ordering = ["warehouse__name", "name"]  # Сортировка по складу и названию области

    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Генерация уникального идентификатора: W<warehouse_id>A<max_id>
            max_id = (
                Area.objects.filter(warehouse=self.warehouse)
                .aggregate(max_id=models.Max("id"))["max_id"]
                or 0
            )
            self.unique_id = f"{self.warehouse.unique_id}{max_id + 1:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_id} - {self.name}"


class Sector(models.Model):
    """Модель для представления сектора внутри области."""
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="sectors",
        verbose_name="Область",
    )
    name = models.CharField(max_length=255, verbose_name="Название сектора")
    unique_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name="Уникальный ID",
    )

    class Meta:
        verbose_name = "Сектор"
        verbose_name_plural = "Секторы"
        ordering = ["area__name", "name"]

    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Генерация уникального идентификатора: W<warehouse_id>A<area_id>S<max_id>
            max_id = (
                Sector.objects.filter(area=self.area)
                .aggregate(max_id=models.Max("id"))["max_id"]
                or 0
            )
            self.unique_id = f"{self.area.warehouse.unique_id}{self.area.unique_id}-{max_id + 1:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_id} - {self.name}"


class Shelf(models.Model):
    """Модель для представления полок внутри сектора."""
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name="shelves",
        verbose_name="Сектор",
    )

    LOWER = 'lower'
    MIDDLE = 'middle'
    UPPER = 'upper'
    FRONT = 'front'

    SURFACE_CHOICES = [
        (LOWER, 'Нижняя'),
        (MIDDLE, 'Средняя'),
        (UPPER, 'Верхняя'),
        (FRONT, 'Передняя'),
    ]
    surface = models.CharField(
        max_length=10,
        choices=SURFACE_CHOICES,
        verbose_name="Расположение полки",
    )
    unique_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Уникальный ID"
    )
    qr_code = models.ImageField(
        upload_to="qr_codes/",
        blank=True,
        null=True,
        verbose_name="QR-код"
    )

    class Meta:
        verbose_name = "Полка"
        verbose_name_plural = "Полки"
        ordering = ["sector__name", "surface"]

    def save(self, *args, **kwargs):
        if not self.unique_id:
            surface_codes = {
                self.LOWER: "H",
                self.MIDDLE: "C",
                self.UPPER: "B",
                self.FRONT: "F",
            }
            surface_code = surface_codes.get(self.surface, "X")
            base_unique_id = (
                f"{self.sector.area.warehouse.unique_id[-2:]}"
                f"{self.sector.area.unique_id[-2:]}"
                f"{self.sector.unique_id[-2:]}"
                f"{surface_code}"
            )
            counter = 1
            unique_id = base_unique_id
            while Shelf.objects.filter(unique_id=unique_id).exists():
                unique_id = f"{base_unique_id}{counter:02d}"
                counter += 1

            self.unique_id = unique_id

        # Генерация QR-кода после определения unique_id
        if not self.qr_code:
            self.generate_and_save_qr_code()

        super().save(*args, **kwargs)

    def generate_and_save_qr_code(self):
        # Генерация QR-кода
        qr = segno.make(f"W{self.unique_id}",micro=False)
        buffer = BytesIO()
        qr.save(buffer, kind='png', scale=5)
        buffer.seek(0)

        # Открываем QR-код как изображение
        qr_image = Image.open(buffer)

        # Создаём текст цепочки с разделением на строки
        text_parts = [
            f"{self.sector.area.warehouse.name}",
            f"{self.sector.area.name} {self.sector.name}",
            f"{self.unique_id}"
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
        file_name = f"{self.unique_id}_qr.png"
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)



