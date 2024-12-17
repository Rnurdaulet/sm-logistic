from django.db import models
from services.qr_code_service import QRCodeService
from services.unique_number_service import UniqueNumberService


class Warehouse(models.Model):
    """Модель для представления склада."""
    name = models.CharField(max_length=255, verbose_name="Название склада")
    location = models.TextField(verbose_name="Местоположение", blank=True, null=True)
    unique_id = models.CharField(max_length=10, unique=True,editable=False,verbose_name="Уникальный ID",)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        ordering = ["name"]  # Упорядочивание по имени

    def save(self, *args, **kwargs):
        # Проверка на уникальность ID только при создании объекта
        if not self.unique_id:
            self.unique_id = UniqueNumberService.generate_unique_id(
                model=Warehouse,
                prefix="W"
            )
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
            self.unique_id = UniqueNumberService.generate_unique_id(
                model=Area,
                prefix=f"{self.warehouse.unique_id}A",
                filters={"warehouse": self.warehouse}
            )
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
            self.unique_id = UniqueNumberService.generate_unique_id(
                model=Sector,
                prefix=f"{self.area.warehouse.unique_id}{self.area.unique_id}-S",
                filters={"area": self.area}
            )
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
        upload_to="warehouse/qr_codes/",
        blank=True,
        null=True,
        verbose_name="QR-код"
    )

    class Meta:
        verbose_name = "Полка"
        verbose_name_plural = "Полки"
        ordering = ["sector__name", "surface"]

    def save(self, *args, **kwargs):
        # Сохраняем объект, чтобы получить первичный ключ и уникальный ID
        if not self.unique_id:
            self.unique_id = UniqueNumberService.generate_surface_unique_id(self)
            super().save(*args, **kwargs)  # Первичное сохранение для получения pk

        # Генерация QR-кода, если его ещё нет
        if not self.qr_code:
            QRCodeService.generate_qr_code(
                instance=self,
                qr_data=f"W{self.unique_id}",
                text_parts=[
                    f"{self.sector.area.warehouse.name}",
                    f"{self.sector.area.name} {self.sector.name}",
                    f"{self.unique_id}"
                ],
                file_prefix="W"
            )
            super().save(update_fields=["qr_code"])  # Сохраняем только QR-код

        # Обычное сохранение (для других изменений)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_id}"
