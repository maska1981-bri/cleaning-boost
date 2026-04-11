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

    readonly_fields = (
        "apartment_max_guests",
        "apartment_beds",
        "apartment_google_maps",
        "apartment_notes",
    )

    fields = (
        "apartment",

        # 👇 BLOCCO IMMOBILE
        "apartment_max_guests",
        "apartment_beds",
        "apartment_google_maps",
        "apartment_notes",

        # 👇 DATI PRENOTAZIONE
        "guest_name",
        "people_count",
        ("double_beds", "single_beds"),
        ("check_in", "check_in_time"),
        ("check_out", "check_out_time"),
        "notes",
    )

    # =========================
    # DATI IMMOBILE (READONLY)
    # =========================

    def apartment_max_guests(self, obj):
        if obj.apartment:
            return obj.apartment.max_guests
        return "-"
    apartment_max_guests.short_description = "Max ospiti immobile"

    def apartment_beds(self, obj):
        if obj.apartment:
            return f"{obj.apartment.double_beds}M / {obj.apartment.single_beds}S"
        return "-"
    apartment_beds.short_description = "Letti totali immobile"

    def apartment_google_maps(self, obj):
        if obj.apartment and obj.apartment.google_maps_url:
            return format_html(
                '<a href="{}" target="_blank">Apri mappa</a>',
                obj.apartment.google_maps_url
            )
        return "-"
    apartment_google_maps.short_description = "Google Maps"

    def apartment_notes(self, obj):
        if obj.apartment and obj.apartment.operational_notes:
            return obj.apartment.operational_notes
        return "-"
    apartment_notes.short_description = "Note operative immobile"


from django.utils.html import format_html