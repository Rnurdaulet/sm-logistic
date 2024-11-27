from django.contrib import admin
from .models import Warehouse, Area, Sector, Shelf


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')
    ordering = ('name',)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse')
    search_fields = ('name', 'warehouse__name')
    list_filter = ('warehouse',)
    autocomplete_fields = ('warehouse',)
    ordering = ('name',)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'area')
    search_fields = ('name', 'area__name', 'area__warehouse__name')
    list_filter = ('area__warehouse', 'area')
    autocomplete_fields = ('area',)
    ordering = ('name',)


@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ('name', 'surface', 'sector')
    search_fields = ('name', 'sector__name', 'sector__area__name', 'sector__area__warehouse__name')
    list_filter = ('surface', 'sector__area__warehouse', 'sector__area')
    autocomplete_fields = ('sector',)
    ordering = ('name',)
