from django.db import models


class Warehouse(models.Model):
    """Модель для представления склада."""
    name = models.CharField(max_length=255, verbose_name="Название склада")
    location = models.TextField(verbose_name="Местоположение", blank=True, null=True)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"
        ordering = ["name"]  # Упорядочивание по имени

    def __str__(self):
        return self.name


class Area(models.Model):
    """Модель для представления области внутри склада."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="areas",
        verbose_name="Склад",
    )
    name = models.CharField(max_length=255, verbose_name="Название области")

    class Meta:
        verbose_name = "Область"
        verbose_name_plural = "Области"
        ordering = ["warehouse__name", "name"]  # Сначала сортировка по складу, затем по названию области

    def __str__(self):
        return f"{self.name} ({self.warehouse.name})"


class Sector(models.Model):
    """Модель для представления сектора внутри области."""
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="sectors",
        verbose_name="Область",
    )
    name = models.CharField(max_length=255, verbose_name="Название сектора")

    class Meta:
        verbose_name = "Сектор"
        verbose_name_plural = "Секторы"
        ordering = ["area__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.area.name})"


class Shelf(models.Model):
    """Модель для представления полок внутри сектора."""
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name="shelves",
        verbose_name="Сектор",
    )
    name = models.CharField(max_length=255, verbose_name="Название полки")

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

    class Meta:
        verbose_name = "Полка"
        verbose_name_plural = "Полки"
        ordering = ["sector__name", "surface", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_surface_display()}) - {self.sector.name}"
