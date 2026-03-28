from django.contrib import admin
from .models import DayNote


@admin.register(DayNote)
class DayNoteAdmin(admin.ModelAdmin):
    list_display = (
        "apartment",
        "date",
        "note_type",
        "notes",
    )

    list_filter = (
        "note_type",
        "date",
    )

    search_fields = (
        "apartment__name",
        "apartment__code",
        "notes",
    )