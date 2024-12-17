from django.core.exceptions import ValidationError
from django.db import models

from services.unique_number_service import UniqueNumberService


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

    def clean(self):
        """
        Проверяет, можно ли изменить статус маршрута на inactive или completed.
        """
        if self.status in ['inactive', 'completed']:
            # Получаем связанные заказы с неподходящими статусами
            problematic_orders = self.orders.filter(status__in=['loading', 'in_transit', 'unloading'])
            if problematic_orders.exists():
                # Генерируем список номеров заказов
                order_numbers = ", ".join(problematic_orders.values_list("order_number", flat=True))
                raise ValidationError(
                    f"Невозможно установить статус '{self.get_status_display()}'. "
                    f"Следующие заказы имеют неподходящий статус: {order_numbers}."
                )

    def save(self, *args, **kwargs):
        """
        Генерация уникального номера маршрута, если он отсутствует, и обновление статусов заказов.
        """
        self.clean()  # Вызываем валидацию перед сохранением
        is_status_changed = False

        if self.pk:
            # Проверяем старый статус маршрута перед сохранением
            old_status = Route.objects.get(pk=self.pk).status
            is_status_changed = old_status != self.status

        # Генерация уникального номера маршрута, если он отсутствует
        if not self.unique_number:
            UniqueNumberService.generate_route_unique_number(self)

        # Если статус изменился, обновляем связанные заказы
        if is_status_changed:
            self.update_order_statuses()

    def update_order_statuses(self):
        """
        Обновляет статусы связанных заказов в зависимости от статуса маршрута.
        """
        new_status_map = {
            'loading': 'loading',
            'on_way': 'in_transit',
            'unloading': 'unloading',
        }

        if self.status in new_status_map:
            new_status = new_status_map[self.status]
            self.orders.filter(status__in=['accepted', 'loading', 'in_transit', 'unloading']).update(status=new_status)

    def __str__(self):
        return f"{self.unique_number} -  ({self.get_status_display()})"
