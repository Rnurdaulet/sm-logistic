from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .services import OrderShelfService


def add_orders_to_shelf_view(request):
    if request.method == "POST":
        order_numbers = request.POST.get("order_numbers", "").split(",")
        shelf_unique_id = request.POST.get("shelf_unique_id", "").strip()

        try:
            result = OrderShelfService.add_orders_to_shelf(
                order_numbers=order_numbers,
                shelf_unique_id=shelf_unique_id
            )
            messages.success(request, result)
        except ValueError as e:
            messages.error(request, str(e))
        return redirect("admin:add_orders_to_shelf")

    return render(request, "admin/add_orders_to_shelf.html")
