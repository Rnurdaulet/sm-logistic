from django.db import models

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


from django.db import models

from django.db import models

class Shelf(models.Model):
    """Модель для представления полок внутри сектора."""
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name="shelves",
        verbose_name="Сектор",
    )

    # Варианты расположения полки
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

    class Meta:
        verbose_name = "Полка"
        verbose_name_plural = "Полки"
        ordering = ["sector__name", "surface"]

    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Определяем код для surface
            surface_codes = {
                self.LOWER: "L",
                self.MIDDLE: "M",
                self.UPPER: "U",
                self.FRONT: "F",
            }
            surface_code = surface_codes.get(self.surface, "X")  # Используем "X", если surface неизвестен

            # Формируем базовый уникальный идентификатор
            base_unique_id = (
                f"{self.sector.area.warehouse.unique_id[-2:]}"  # Последние 2 символа ID склада
                f"{self.sector.area.unique_id[-2:]}"           # Последние 2 символа ID области
                f"{self.sector.unique_id[-2:]}"                # Последние 2 символа ID сектора
                f"{surface_code}"                              # Код поверхности
            )

            # Проверяем уникальность и добавляем суффикс, если необходимо
            counter = 1
            unique_id = base_unique_id
            while Shelf.objects.filter(unique_id=unique_id).exists():
                unique_id = f"{base_unique_id}{counter:02d}"
                counter += 1

            self.unique_id = unique_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_id} - {self.get_surface_display()}"



