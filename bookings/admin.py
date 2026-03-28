from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "apartment",
        "guest_name",
        "people_count",
        "double_beds",
        "single_beds",
        "check_in",
        "check_in_time",
        "check_out",
        "check_out_time",
    )

    list_filter = (
        "check_in",
        "check_out",
        "apartment",
    )

    search_fields = (
        "guest_name",
        "apartment__name",
        "apartment__code",
        "notes",
    )

    fields = (
        "apartment",
        "guest_name",
        "people_count",
        ("double_beds", "single_beds"),
        ("check_in", "check_in_time"),
        ("check_out", "check_out_time"),
        "notes",
    )