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
        """
        if not self.unique_number:
            creation_date = self.created_at or now()
            self.created_at = creation_date  # Устанавливаем дату создания, если не задана

            # Сохраняем объект, чтобы получить первичный ключ (id)
            super().save(*args, **kwargs)

            # Получаем ID последнего заказа за текущий день
            start_of_day = creation_date.date()
            unique_id = (
                    Route.objects.filter(created_at__date=start_of_day)
                    .aggregate(max_id=models.Max("id"))["max_id"] or 0
            )

            # Формируем номер заказа
            self.unique_number = f"{creation_date.strftime('%d%m%y')}-{self.truck.plate_number}-{unique_id + 1:02d}"

            # Сохраняем снова с обновленным уникальным номером
            super().save(update_fields=["unique_number"])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_number}"
