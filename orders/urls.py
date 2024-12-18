from django.urls import path
from .views import add_orders_to_shelf_view

urlpatterns = [
    path("add-orders-to-shelf/", add_orders_to_shelf_view, name="add_orders_to_shelf"),
]
