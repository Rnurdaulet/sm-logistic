from django.db import models
from django.utils.timezone import now


class Truck(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название фуры")
    plate_number = models.CharField(max_length=20, unique=True, verbose_name="Госномер")

    class Meta:
        verbose_name = "Фура"
        verbose_name_plural = "Фуры"
        ordering = ['name']  # Сортировка по имени фуры

    def __str__(self):
        return f"{self.name} ({self.plate_number})"


class Route(models.Model):
    STATUS_CHOICES = [
        ('inactive', 'Неактивен'),
        ('loading', 'Погрузка'),
        ('on_way', 'В пути'),
        ('unloading', 'Выгрузка'),
        ('completed', 'Завершен'),
    ]

    truck = models.ForeignKey(
        Truck,
        on_delete=models.CASCADE,
        related_name="routes",
        verbose_name="Фура"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='inactive',
        verbose_name="Статус маршрута"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    unique_number = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        blank=True,
        verbose_name="Уникальный номер"
    )

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
        ordering = ['-created_at']  # Сортировка по дате создания

    def save(self, *args, **kwargs):
        """
        Генерация уникального номера маршрута, если он отсутствует.
        Формат: {Название фуры}-{ДеньМесяц}-{ID}
        """
        if not self.unique_number:
            current_date = now()
            day = current_date.strftime('%d')
            month = current_date.strftime('%m')
            super().save(*args, **kwargs)  # Сохранение для получения ID
            self.unique_number = f"{self.truck.name}-{day}{month}-{self.id}"
            super().save(update_fields=['unique_number'])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_number}"
