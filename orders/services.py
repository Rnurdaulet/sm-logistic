from django.urls import reverse
from django.http import HttpResponseRedirect
from warehouse.models import Warehouse, Area, Sector, Shelf
from trucks.models import Route


def get_filtered_orders_url(model_instance, model_field, admin_url_name, title_prefix):
    """
    Генерирует URL для фильтрации заказов по связанным объектам.
    """
    url = reverse(admin_url_name)
    query_string = f"?{model_field}__id__exact={model_instance.id}"
    title = f"{title_prefix} {model_instance}"
    return url + query_string, title


def redirect_with_custom_title(request, url, title):
    """
    Редиректит с сохранением заголовка.
    """
    request.session['custom_title'] = title
    return HttpResponseRedirect(url)
