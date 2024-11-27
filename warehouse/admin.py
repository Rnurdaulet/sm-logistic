from django.contrib import admin
from .models import Warehouse, Area, Sector, Shelf

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse')

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'area')

@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ('name', 'surface', 'sector')
    list_filter = ('surface',)
