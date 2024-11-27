from django.db import models


class Warehouse(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название склада")
    location = models.TextField(verbose_name="Местоположение", blank=True, null=True)

    def __str__(self):
        return self.name


class Area(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="areas", verbose_name="Склад")
    name = models.CharField(max_length=255, verbose_name="Название области")

    def __str__(self):
        return f"{self.name} ({self.warehouse.name})"


class Sector(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="sectors", verbose_name="Область")
    name = models.CharField(max_length=255, verbose_name="Название сектора")

    def __str__(self):
        return f"{self.name} ({self.area.name})"


class Shelf(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="shelves", verbose_name="Сектор")
    name = models.CharField(max_length=255, verbose_name="Название полки")
    LOWER = 'lower'
    MIDDLE = 'middle'
    UPPER = 'upper'
    FRONT = 'front'

    SURFACE_CHOICES = [
        (LOWER, 'Нижняя'),
        (MIDDLE, 'Средняя'),
        (UPPER, 'Верхняя'),
        (FRONT, 'Поверхность'),
    ]
    surface = models.CharField(max_length=10, choices=SURFACE_CHOICES, verbose_name="Полка")

    def __str__(self):
        return f"{self.name} ({self.surface}) - {self.sector.name}"
