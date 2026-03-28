from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "phone", "email", "is_active")
    search_fields = ("name", "phone", "email", "user__username")
    list_filter = ("is_active",)
    autocomplete_fields = ("user",)