from django.contrib import admin, messages
from django.urls import path
from unfold.views import UnfoldModelAdminViewMixin
from django.views.generic import TemplateView
from .models import DummyModel
from orders.services import OrderShelfService


class AddOrdersToShelfView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Добавить заказы на полку"
    permission_required = ()
    template_name = "admin/add_orders_to_shelf.html"

    def post(self, request, *args, **kwargs):
        order_numbers = request.POST.get("order_numbers", "")
        shelf_unique_id = request.POST.get("shelf_unique_id", "").strip()

        # Проверяем, что номера заказов не пустые
        if not order_numbers.strip():
            messages.error(request, "Номера заказов не могут быть пустыми.")
            return self.render_to_response(self.get_context_data(request=request))

        # Проверяем, что ID полки не пустой
        if not shelf_unique_id:
            messages.error(request, "Уникальный ID полки обязателен.")
            return self.render_to_response(self.get_context_data(request=request))

        # Удаляем лишние пробелы и кавычки из номеров заказов
        order_numbers = [num.strip().strip("'").strip('"') for num in order_numbers.split(",") if num.strip()]

        # Проверяем, что список заказов не пуст после очистки
        if not order_numbers:
            messages.error(request, "Номера заказов некорректны или отсутствуют.")
            return self.render_to_response(self.get_context_data(request=request))

        try:
            result = OrderShelfService.add_orders_to_shelf(
                order_numbers=order_numbers,
                shelf_unique_id=shelf_unique_id
            )
            messages.success(request, result)
        except ValueError as e:
            messages.error(request, str(e))

        return self.render_to_response(self.get_context_data(request=request))


class DummyModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        custom_urls = [
            path(
                "add-orders-to-shelf/",
                AddOrdersToShelfView.as_view(model_admin=self),  # Передаём model_admin
                name="add_orders_to_shelf",
            ),
        ]
        return custom_urls + super().get_urls()



admin.site.register(DummyModel, DummyModelAdmin)
