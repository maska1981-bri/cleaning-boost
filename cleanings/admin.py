from django.contrib import admin
from .models import Cleaning, CleaningAttachment


class CleaningAttachmentInline(admin.TabularInline):
    model = CleaningAttachment
    extra = 0
    fields = ("file", "note", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(Cleaning)
class CleaningAdmin(admin.ModelAdmin):
    list_display = (
        "apartment",
        "date",
        "status",
        "booking",
        "people_count",
        "double_beds_count",
        "single_beds_count",
        "total_cost",
    )
    list_filter = ("status", "date", "apartment")
    search_fields = ("apartment__name",)
    filter_horizontal = ("employees",)
    inlines = [CleaningAttachmentInline]

    def save_model(self, request, obj, form, change):
        obj.apply_apartment_default_costs(force=False)
        super().save_model(request, obj, form, change)


@admin.register(CleaningAttachment)
class CleaningAttachmentAdmin(admin.ModelAdmin):
    list_display = ("cleaning", "filename", "note", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("cleaning__apartment__name", "note")

    def filename(self, obj):
        return obj.filename