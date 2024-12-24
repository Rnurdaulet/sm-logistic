from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Count, Sum
from django.utils.safestring import mark_safe
from orders.models import Order
from datetime import timedelta
from django.utils.timezone import now


def dashboard_callback(request, context):
    # Текущая дата
    today = now().date()

    # Даты для анализа
    last_week_start = today - timedelta(days=14)
    last_week_end = today - timedelta(days=7)
    this_week_start = today - timedelta(days=7)
    this_week_end = today

    # Заказы за текущую и прошлую недели
    def get_weekly_count(status, start_date, end_date):
        return Order.objects.filter(status=status, date__date__gte=start_date, date__date__lte=end_date).count()

    # Текущая неделя
    this_week_accepted = get_weekly_count("accepted", this_week_start, this_week_end)
    this_week_in_warehouse = get_weekly_count("in_warehouse", this_week_start, this_week_end)
    this_week_completed = get_weekly_count("completed", this_week_start, this_week_end)

    # Предыдущая неделя
    last_week_accepted = get_weekly_count("accepted", last_week_start, last_week_end)
    last_week_in_warehouse = get_weekly_count("in_warehouse", last_week_start, last_week_end)
    last_week_completed = get_weekly_count("completed", last_week_start, last_week_end)

    # Возвраты и отмены за текущую неделю
    this_week_returns = get_weekly_count("return", this_week_start, this_week_end)
    this_week_canceled = get_weekly_count("canceled", this_week_start, this_week_end)

    # Процент безналичных оплат
    total_orders = Order.objects.count()
    total_cashless_orders = Order.objects.filter(is_cashless=True).count()
    cashless_percentage = (total_cashless_orders / total_orders * 100) if total_orders > 0 else 0

    # Расчёт процентного изменения
    def calculate_change(current, previous):
        if previous > 0:
            return ((current - previous) / previous) * 100
        return 100.0 if current > 0 else 0

    accepted_change = calculate_change(this_week_accepted, last_week_accepted)
    in_warehouse_change = calculate_change(this_week_in_warehouse, last_week_in_warehouse)
    completed_change = calculate_change(this_week_completed, last_week_completed)

    # KPI 1: Метрики по статусам
    kpi_data = [
        {
            "title": "Принято",
            "metric": f"{intcomma(this_week_accepted)}",
            "footer": mark_safe(
                f'<strong class="{"text-green-700 font-semibold dark:text-green-400" if accepted_change >= 0 else "text-red-700 font-semibold dark:text-red-400"}">'
                f'{accepted_change:+.2f}%</strong>&nbsp;прогресс с прошлой недели'
            ),
        },
        {
            "title": "На складе",
            "metric": f"{intcomma(this_week_in_warehouse)}",
            "footer": mark_safe(
                f'<strong class="{"text-green-700 font-semibold dark:text-green-400" if in_warehouse_change >= 0 else "text-red-700 font-semibold dark:text-red-400"}">'
                f'{in_warehouse_change:+.2f}%</strong>&nbsp;прогресс с прошлой недели'
            ),
        },
        {
            "title": "Выдано",
            "metric": f"{intcomma(this_week_completed)}",
            "footer": mark_safe(
                f'<strong class="{"text-green-700 font-semibold dark:text-green-400" if completed_change >= 0 else "text-red-700 font-semibold dark:text-red-400"}">'
                f'{completed_change:+.2f}%</strong>&nbsp;прогресс с прошлой недели'
            ),
        },

    ]
    kpi_data1 = [
        {
            "title": "Возвраты",
            "metric": f"{intcomma(this_week_returns)}",
            "footer": mark_safe('<strong class="text-blue-700 font-semibold dark:text-blue-400">Обновлено</strong>'),
        },
        {
            "title": "Отменено",
            "metric": f"{intcomma(this_week_canceled)}",
            "footer": mark_safe('<strong class="text-red-700 font-semibold dark:text-red-400">Обновлено</strong>'),
        },
        {
            "title": "Процент безналичных оплат",
            "metric": f"{cashless_percentage:.2f}%",
            "footer": mark_safe(
                '<strong class="text-green-700 font-semibold dark:text-green-400">Безналичный расчёт</strong>'),
        },
    ]

    # KPI 2: Общая информация
    total_items_in_warehouse = Order.objects.filter(status="in_warehouse").count()
    total_paid = Order.objects.filter(status="in_warehouse").aggregate(total_paid=Sum("paid_amount"))["total_paid"] or 0
    total_price = Order.objects.filter(status="in_warehouse").aggregate(total_price=Sum("price"))["total_price"] or 0
    total_due = total_price - total_paid

    kpi_data2 = [
        {
            "title": "Общее количество товаров на складе",
            "metric": f"{intcomma(total_items_in_warehouse)}",
            "footer": mark_safe('<strong class="text-blue-700 font-semibold dark:text-blue-400">Обновлено</strong>'),
        },
        {
            "title": "Общая сумма",
            "metric": f"{intcomma(total_paid)} ₸",
            "footer": mark_safe('<strong class="text-blue-700 font-semibold dark:text-blue-400">Обновлено</strong>'),
        },
        {
            "title": "Общая задолженность",
            "metric": f"{intcomma(total_due)} ₸",
            "footer": mark_safe('<strong class="text-red-700 font-semibold dark:text-red-400">Неоплачено</strong>'),
        },
    ]

    # Добавление данных в контекст
    context.update({
        "kpi": kpi_data,
        "kpi1": kpi_data1,
        "kpi2": kpi_data2,
    })

    return context