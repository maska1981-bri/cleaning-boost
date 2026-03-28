from django.contrib import admin
from .models import LaundryItem, LaundryInventory, LaundryMovement


@admin.register(LaundryItem)
class LaundryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "active")
    search_fields = ("name", "code")
    list_filter = ("active",)


@admin.register(LaundryInventory)
class LaundryInventoryAdmin(admin.ModelAdmin):
    list_display = ("item", "quantity")
    search_fields = ("item",)


@admin.register(LaundryMovement)
class LaundryMovementAdmin(admin.ModelAdmin):
    list_display = ("date", "item", "movement_type", "quantity", "created_at")
    list_filter = ("movement_type", "date")
    search_fields = ("item",)