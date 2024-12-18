import os
from functools import lru_cache, partial

from django.contrib import admin
from django.db.models import F
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse, HttpResponseRedirect

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import action
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm

from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin

from xhtml2pdf import pisa
from xhtml2pdf.files import pisaFileObject

from sm_project import settings
from .models import Order
from .resources import OrderResource


class PaymentStatusFilter(SimpleListFilter):
    title = 'Статус оплаты'
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        """Возвращает параметры фильтра."""
        return [
            ('paid', 'Оплачено'),
            ('unpaid', 'Неоплачено')
        ]

    def queryset(self, request, queryset):
        """Фильтрует записи на основе выбранного параметра."""
        match self.value():
            case 'paid':
                return queryset.filter(price=F('paid_amount'))
            case 'unpaid':
                return queryset.exclude(price=F('paid_amount'))
        return queryset


class TruckFilter(SimpleListFilter):
    title = 'Фура'
    parameter_name = 'truck'

    def lookups(self, request, model_admin):
        """Возвращает список доступных фур для фильтрации."""
        from trucks.models import Truck  # Импортируем модель Truck
        trucks = Truck.objects.all()
        return [(truck.id, f"{truck.plate_number}") for truck in trucks]

    def queryset(self, request, queryset):
        """Фильтрует записи на основе выбранной фуры."""
        if self.value():
            return queryset.filter(route__truck_id=self.value())
        return queryset


# Общая функция фильтрации заказов
def filter_orders(request, field, value, title_prefix, admin_url="admin:orders_order_changelist"):
    """
    Генерирует URL для фильтрации заказов и перенаправляет на страницу с заголовком.
    """
    url = reverse(admin_url)
    query_string = f"?{field}={value}"
    request.session['custom_title'] = f"{title_prefix} для {value}"
    return HttpResponseRedirect(f"{url}{query_string}")


# Админка OrderAdmin

@admin.register(Order)
class OrderAdmin(ModelAdmin, SimpleHistoryAdmin, ImportExportModelAdmin):
    """
    Админка для модели заказов с кастомными действиями и фильтрацией.
    """
    resource_class = OrderResource
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm
    date_hierarchy = "date"
    actions_detail = ["generate_pdf"]
    list_filter_submit = True
    list_filter_sheet = False
    list_fullwidth = True
    warn_unsaved_form = True
    compressed_fields = True

    autocomplete_fields = ('sender', 'receiver', 'shelf', 'route')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'date', 'add_full_payment_button')
    list_display = ('order_number', 'sender', 'receiver', 'display_payment_status', 'route', 'shelf', 'display_status',)

    list_filter = (("date", RangeDateFilter),'is_cashless', PaymentStatusFilter,TruckFilter)

    search_fields = (
        'order_number',
        'sender__full_name',
        'sender__phone_numbers__number',
        'receiver__full_name',
        'receiver__phone_numbers__number',
        'route__unique_number'
    )

    fieldsets = (
        ("Основная информация", {
            'fields': ('order_number', 'route', 'status', 'sender', 'receiver', 'comment', 'image')
        }),
        ("Детали заказа", {
            'fields': ('seat_count', 'is_cashless', 'price', 'add_full_payment_button', 'paid_amount',)
        }),
        ("QR", {
            'fields': ('qr_code',)
        }),
        ("Склад", {
            'fields': ('shelf',)
        }),
        ("Дополнительно", {
            'fields': ('date', 'created_at', 'updated_at',),
            'classes': ('collapse',),
        }),
    )

    # Добавляем кастомные URL
    def get_urls(self):
        """
        Добавляет дополнительные маршруты для фильтрации заказов.
        """
        custom_filter_routes = [
            ('by-route/<int:value>/', 'route_id', 'Маршрут'),
            ('by-warehouse/<int:value>/', 'shelf__sector__area__warehouse_id', 'Склад'),
            ('by-area/<int:value>/', 'shelf__sector__area_id', 'Зона'),
            ('by-sector/<int:value>/', 'shelf__sector_id', 'Сектор'),
            ('by-shelf/<int:value>/', 'shelf_id', 'Полка'),
        ]

        custom_urls = [
            path(
                route,
                self.admin_site.admin_view(
                    partial(filter_orders, field=field, title_prefix=title)
                ),
                name=f"orders_{field}"
            )
            for route, field, title in custom_filter_routes
        ]

        return custom_urls + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        """
        Настраивает заголовок страницы списка заказов.
        """
        extra_context = extra_context or {}
        extra_context['title'] = request.session.pop('custom_title', 'Список заказов')
        return super().changelist_view(request, extra_context=extra_context)

    # Кнопка "Оплата полностью"

    def add_full_payment_button(self, obj):
        """
        Кнопка для установки полной оплаты.
        """
        button_html = """
        <button type="button" class="bg-primary-600 block border border-transparent font-medium 
            px-3 py-2 rounded-md text-white w-full lg:w-auto" 
            style="margin-top: 10px; padding: 10px;" 
            onclick="setFullPayment()">
            Оплата полностью
        </button>
        """
        script_html = """
        <script>
            function setFullPayment() {
                const priceField = document.getElementById('id_price');
                const paidAmountField = document.getElementById('id_paid_amount');
                if (priceField && paidAmountField) {
                    paidAmountField.value = priceField.value;
                }
            }
        </script>
        """
        return mark_safe(button_html + script_html)

    add_full_payment_button.short_description = "Оплата полностью"

    @admin.display(description="Оплачено")
    def display_payment_status(self, instance):
        if instance.price == instance.paid_amount:
            return f"{int(instance.price)} ₸"
        else:
            return f"-{instance.price - instance.paid_amount} ₸"

    @admin.display(description="Статус")
    def display_status(self, instance):
        # Определяем базовые стили как атрибут класса
        base_style = ("display: flex; align-items: center; justify-content: left; "
                      "padding: 6px 6px; padding-left: 10px; border-radius: 6px; "
                      "font-size: 14px; font-weight: 500; gap: 6px;")
        icon_base_style = "font-size: 18px; vertical-align: middle;"

        # Определяем стили и иконки для статусов
        status_styles = {
            'accepted': ("#4e79a7; color: white;", "done"),
            'loading': ("#f8c471; color: black;", "hourglass_top"),
            'in_transit': ("#6fbf73; color: white;", "local_shipping"),
            'unloading': ("#b0a8b9; color: black;", "unarchive"),
            'in_warehouse': ("#555e6c; color: white;", "warehouse"),
            'completed': ("#88d0a0; color: black;", "check_circle"),
            'canceled': ("#bf616a; color: white;", "cancel"),
        }

        # Кэшируем выборку статусов для оптимизации
        @lru_cache
        def get_status_dict():
            return dict(Order.STATUS_CHOICES)

        # Получаем стиль и иконку
        style, icon = status_styles.get(instance.status, ("#d1d5db; color: black;", ""))
        status_display = get_status_dict().get(instance.status, instance.status)

        # Генерируем HTML с использованием шаблона
        return mark_safe(
            f"""
            <div style="{base_style} background-color: {style}">
                <span class="material-symbols-outlined" style="{icon_base_style}">{icon}</span>
                <span>{status_display}</span>
            </div>
            """
        )

    @action(
        description="Скачать чек",
        url_path="generate_pdf",
        permissions=["generate_pdf"],
    )
    def generate_pdf(self, request, queryset=None, **kwargs):
        """
        Генерация PDF для выбранных заказов.
        """
        if pisa is None:
            return HttpResponse(
                "Библиотека xhtml2pdf не установлена. Пожалуйста, установите её с помощью 'pip install xhtml2pdf'.",
                status=500)

        # Если queryset отсутствует, пробуем получить один объект по object_id
        if queryset is None:
            object_id = kwargs.get("object_id")
            if object_id:
                queryset = self.model.objects.filter(pk=object_id)
            else:
                return HttpResponse("Не указан объект или выборка для генерации PDF.", status=400)

        if not queryset.exists():
            return HttpResponse("Нет доступных заказов для генерации PDF.", status=400)

        # Подготовка контекста для рендера шаблона
        context = {
            'orders': queryset,
            'company_name': "Перевозчик \u00abСауле \u2013 Марат\u00bb",
            'contact_details': {
                'almaty': {
                    'address': "Рынок \u00abSalem\u00bb, Ангарская 107",
                    'phone': "8778 869 5454, 8702 199 9507",
                },
                'astana': {
                    'address': "ул. Пушкина 35",
                    'working_hours': "9:00 - 14:00",
                }
            },
            'notes': [
                "Звонить через день после сдачи товара!",
                "Выдача товара строго по квитанции!",
                "Товар нужно забирать в день прибытия!",
                "Хранение товара на складе платное!!!",
                "Минимальная стоимость перевозки груза от 3000 тг",
            ]
        }

        # Рендер HTML-шаблона
        html = render_to_string('order_pdf_template.html', context)

        # Генерация PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orders.pdf"'

        pisa_status = pisa.CreatePDF(
            src=html,
            dest=response,
            encoding='utf-8',  # Обеспечивает поддержку кириллицы
            link_callback=link_callback)

        # Проверка ошибок при генерации PDF
        if pisa_status.err:
            return HttpResponse("Ошибка при генерации PDF", status=500)

        return response

    def has_generate_pdf_permission(self, request, obj=None):
        """
        Проверяет, имеет ли пользователь доступ к действию custom_actions_detail.
        """
        # Логика проверки прав пользователя.
        # Например, доступ только администраторам:
        return request.user.is_superuser


def link_callback(uri, rel):
    # use short variable names
    sUrl = settings.STATIC_URL  # Typically /static/
    sRoot = settings.STATICFILES_DIRS[0]  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL  # Typically /static/media/
    mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/
    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        path = uri

    pisaFileObject.getNamedFile = lambda self: path

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))

    print(path)
    return path
