from django.contrib import admin
from django.http import HttpResponseRedirect
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

    def response_add(self, request, obj, post_url_continue=None):
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url:
            return HttpResponseRedirect(next_url)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url:
            return HttpResponseRedirect(next_url)
        return super().response_change(request, obj)

    def render_change_form(self, request, context, *args, **kwargs):
        context["extra_next"] = request.GET.get("next", "")
        return super().render_change_form(request, context, *args, **kwargs)


@admin.register(CleaningAttachment)
class CleaningAttachmentAdmin(admin.ModelAdmin):
    list_display = ("cleaning", "filename", "note", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("cleaning__apartment__name", "note")

    def filename(self, obj):
        return obj.filename