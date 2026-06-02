from django.contrib import admin

from catalog.models import Item, Manufacturer


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "state")
    search_fields = ("name",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "manufacturer", "created_at")
    list_select_related = ("manufacturer",)
    search_fields = ("name",)
    list_filter = ("manufacturer",)
