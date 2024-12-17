# services/unique_number_service.py
from django.utils import timezone
from django.db.models import Max

class UniqueNumberService:
    @staticmethod
    def generate_unique_number(model, date_field="created_at", prefix_format="%d%m%y", id_field="id"):
        """
        Генерирует уникальный номер для записи.

        Args:
            model: Модель Django для запроса.
            date_field: Поле даты создания записи.
            prefix_format: Формат для создания префикса на основе даты.
            id_field: Поле для уникального идентификатора (например, id).

        Returns:
            Уникальный номер в формате "дата-уникальный_ID".
        """
        creation_date = timezone.now()
        start_of_day = creation_date.date()
        unique_id = (
            model.objects.filter(**{f"{date_field}__date": start_of_day})
            .aggregate(max_id=Max(id_field))["max_id"] or 0
        )
        return f"{creation_date.strftime(prefix_format)}-{unique_id + 1:04d}"

    @staticmethod
    def generate_surface_unique_id(instance, unique_field="unique_id"):
        """
        Генерирует уникальный ID на основе объекта модели (instance), автоматически строя surface-коды и компоненты.

        Args:
            instance: Экземпляр модели, для которого генерируется ID.
            unique_field: Поле, по которому проверяется уникальность.

        Returns:
            Строка уникального идентификатора.
        """
        surface_codes = {
            instance.LOWER: "H",
            instance.MIDDLE: "C",
            instance.UPPER: "B",
            instance.FRONT: "F",
        }

        base_components = [
            instance.sector.area.warehouse.unique_id,
            instance.sector.area.unique_id,
            instance.sector.unique_id,
        ]
        surface_code = surface_codes.get(instance.surface, "X")

        base_unique_id = "".join(comp[-2:] for comp in base_components) + surface_code
        counter = 1
        unique_id = base_unique_id
        model = instance.__class__
        while model.objects.filter(**{unique_field: unique_id}).exists():
            unique_id = f"{base_unique_id}{counter:02d}"
            counter += 1

        return unique_id

    @staticmethod
    def generate_route_unique_number(instance, truck_plate_field="truck", unique_field="unique_number"):
        """
        Генерирует уникальный номер для маршрута на основе даты, номера машины и ID.

        Args:
            instance: Экземпляр модели.
            truck_plate_field: Поле, содержащее информацию о номере машины.
            unique_field: Поле, куда сохраняется уникальный номер.

        Returns:
            Строка уникального номера маршрута.
        """
        from django.utils.timezone import now

        # Устанавливаем дату создания, если она ещё не определена
        creation_date = instance.created_at or now()
        instance.created_at = creation_date

        # Первичное сохранение для получения `pk`
        instance.save()

        # Формируем уникальный ID для маршрута
        start_of_day = creation_date.date()
        model = instance.__class__
        unique_id = (
            model.objects.filter(created_at__date=start_of_day)
            .aggregate(max_id=Max("id"))["max_id"] or 0
        )

        # Генерация номера
        plate_number = getattr(instance.truck, "plate_number", "NO-PLATE")
        unique_number = f"{creation_date.strftime('%d%m%y')}-{plate_number}-{unique_id + 1:02d}"

        # Сохранение номера
        setattr(instance, unique_field, unique_number)
        instance.save(update_fields=[unique_field])

        return unique_number

    @staticmethod
    def generate_unique_id(model, prefix="", filters=None, id_field="id"):
        """
        Генерирует уникальный ID на основе максимального ID в модели с опциональными фильтрами.

        Args:
            model: Модель Django, для которой генерируется уникальный ID.
            prefix: Префикс для ID (например, W, A, S).
            filters: Словарь фильтров для ограничения запроса.
            id_field: Поле для поиска максимального ID.

        Returns:
            Строка уникального идентификатора.
        """
        filters = filters or {}
        max_id = model.objects.filter(**filters).aggregate(max_id=Max(id_field))["max_id"] or 0
        return f"{prefix}{max_id + 1:02d}"
