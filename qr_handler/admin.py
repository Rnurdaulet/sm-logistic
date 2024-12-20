import json

from django.contrib import admin, messages
from django.urls import path
from unfold.views import UnfoldModelAdminViewMixin
from django.views.generic import TemplateView
from .models import DummyModel
from orders.services import OrderShelfService


class AddOrdersToShelfViewQR(UnfoldModelAdminViewMixin, TemplateView):
    title = "Добавить заказы на полку"
    permission_required = ()
    template_name = "admin/add_orders_to_shelf_qr.html"

    def parse_json_field(self, raw_data, field_name):
        """
        Парсит JSON-данные и извлекает значение ключа "value".
        Если данные не JSON или некорректны, возвращает как есть.
        """
        try:
            parsed_data = json.loads(raw_data)
            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                value = parsed_data[0].get("value")
                if not value:
                    raise ValueError(f"Значение ключа 'value' для {field_name} отсутствует или пустое.")
                return value
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            print(f"Ошибка обработки JSON для {field_name}: {e}")
        return raw_data  # Возвращаем данные как есть, если парсинг не удался

    def parse_order_numbers(self, raw_data):
        """
        Парсит JSON-данные номеров заказов и возвращает список значений ключа "value".
        """
        try:
            parsed_data = json.loads(raw_data)
            return [item["value"] for item in parsed_data if "value" in item]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []  # Возвращаем пустой список при ошибке

    def post(self, request, *args, **kwargs):
        # Получаем данные из запроса
        order_numbers_raw = request.POST.get("order_numbers", "")
        shelf_unique_id_raw = request.POST.get("shelf_unique_id", "")

        # Обрабатываем уникальный ID полки
        shelf_unique_id = self.parse_json_field(shelf_unique_id_raw, "shelf_unique_id")
        if not shelf_unique_id:
            messages.error(request, "Уникальный ID полки обязателен.")
            return self.render_to_response(self.get_context_data(request=request))

        # Обрабатываем номера заказов
        order_numbers = self.parse_order_numbers(order_numbers_raw)
        if not order_numbers:
            messages.error(request, "Номера заказов некорректны или отсутствуют.")
            return self.render_to_response(self.get_context_data(request=request))

        # Выполняем логику добавления заказов
        try:
            result = OrderShelfService.add_orders_to_shelf(
                order_numbers=order_numbers,
                shelf_unique_id=shelf_unique_id
            )
            messages.success(request, result)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "Произошла непредвиденная ошибка при добавлении заказов.")

        return self.render_to_response(self.get_context_data(request=request))

class DummyModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        custom_urls = [
            path(
                "add-orders-to-shelf-qr/",
                AddOrdersToShelfViewQR.as_view(model_admin=self),  # Передаём model_admin
                name="add_orders_to_shelf_qr",
            ),
        ]
        return custom_urls + super().get_urls()


admin.site.register(DummyModel, DummyModelAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.admin import ModelAdmin

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
