from import_export import resources
from .models import Order


class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "status",
            "sender",
            "receiver",
            "price",
            "paid_amount",
            "date",
            "created_at",
            "updated_at",
        )
        export_order = (
            "id",
            "order_number",
            "status",
            "sender",
            "receiver",
            "price",
            "paid_amount",
            "date",
            "created_at",
            "updated_at",
        )
