from django.contrib import admin
from .models import CondominiumCleaningRule


@admin.register(CondominiumCleaningRule)
class CondominiumCleaningRuleAdmin(admin.ModelAdmin):

    list_display = (
        "apartment",
        "frequency",
        "start_date",
        "end_date",
        "work_hours",
        "is_active",
    )

    list_filter = (
        "frequency",
        "is_active",
    )

    search_fields = (
        "apartment__name",
    )