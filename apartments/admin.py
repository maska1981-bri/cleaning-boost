from django.contrib import admin
from .models import Apartment, ApartmentPhoto


class ApartmentPhotoInline(admin.TabularInline):
    model = ApartmentPhoto
    extra = 1
    fields = ("image", "caption", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    inlines = [ApartmentPhotoInline]

    list_display = (
        "code",
        "name",
        "customer",
        "property_type",
        "is_active",
        "default_cleaning_cost",
        "default_fixed_kit_cost",
        "default_per_person_kit_cost",
        "default_double_bed_cost",
        "default_single_bed_cost",
        "default_mat_cost",
        "default_extra_cost",
    )

    list_filter = (
        "property_type",
        "is_active",
        "customer",
    )

    search_fields = (
        "code",
        "name",
        "address",
        "customer__name",
        "customer__company_name",
    )

    fields = (
        "customer",
        ("code", "name"),
        ("property_type", "is_active"),
        "address",
        ("max_guests", "double_beds", "single_beds"),
        "google_maps_url",
        "operational_notes",
        ("default_cleaning_cost", "default_fixed_kit_cost"),
        ("default_per_person_kit_cost", "default_double_bed_cost"),
        ("default_single_bed_cost", "default_mat_cost"),
        "default_extra_cost",
    )


@admin.register(ApartmentPhoto)
class ApartmentPhotoAdmin(admin.ModelAdmin):
    list_display = ("apartment", "caption", "created_at")
    list_filter = ("apartment",)
    search_fields = ("apartment__name", "apartment__code", "caption")