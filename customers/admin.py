from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company_name",
        "email",
        "phone",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "company_name",
        "email",
        "phone",
        "vat_number",
        "tax_code",
    )

    fields = (
        "name",
        "company_name",
        ("vat_number", "tax_code"),
        ("email", "phone"),
        "address",
        "notes",
        "is_active",
    )