from django.contrib import admin
from .models import Truck, Route


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('name', 'plate_number')
    search_fields = ('name', 'plate_number')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('truck', 'unique_number', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'truck')
    search_fields = ('truck__name', 'unique_number')
