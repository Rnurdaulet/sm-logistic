from django.core.exceptions import ValidationError
from django.db import models
from services.unique_number_service import UniqueNumberService


class Truck(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название фуры")
    plate_number = models.CharField(max_length=20, unique=True, verbose_name="Госномер")

    class Meta:
        verbose_name = "Фура"
        verbose_name_plural = "Фуры"
        ordering = ['name']

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
        ordering = ['-created_at']

    def clean(self):
        """Проверка на невозможность перевода маршрута в 'inactive' или 'completed' при активных заказах."""
        if self.status in ['inactive', 'completed']:
            problematic_orders = self.orders.filter(status__in=['loading', 'in_transit', 'unloading'])
            if problematic_orders.exists():
                order_numbers = ", ".join(problematic_orders.values_list("order_number", flat=True))
                raise ValidationError(
                    f"Невозможно установить статус '{self.get_status_display()}'. "
                    f"Заказы с неподходящим статусом: {order_numbers}."
                )

    def save(self, *args, **kwargs):
        """
        Проверка данных, генерация номера маршрута и обновление связанных заказов при изменении статуса.
        """
        self.clean()  # Валидируем данные перед сохранением

        if not self.unique_number:
            self.unique_number = UniqueNumberService.generate_route_unique_number(self)

        # Проверка и обновление статусов заказов
        if self.pk:
            old_status = Route.objects.get(pk=self.pk).status
            if old_status != self.status:
                self._update_orders_on_status_change()

        super().save(*args, **kwargs)

    def _update_orders_on_status_change(self):
        """Обновляет статусы заказов при изменении статуса маршрута."""
        status_map = {
            'loading': 'loading',
            'on_way': 'in_transit',
            'unloading': 'unloading',
        }
        new_status = status_map.get(self.status)
        if new_status:
            self.orders.filter(status__in=['accepted', 'loading', 'in_transit', 'unloading']).update(status=new_status)

    def __str__(self):
        return f"{self.unique_number} - ({self.get_status_display()})"
