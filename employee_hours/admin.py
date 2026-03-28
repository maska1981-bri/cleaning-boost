from django.contrib import admin
from .models import WorkLog, HourlyRate


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'hours', 'note', 'created_at')
    list_filter = ('employee', 'date')
    search_fields = ('employee__name', 'note')
    ordering = ('-date', 'employee__id')


@admin.register(HourlyRate)
class HourlyRateAdmin(admin.ModelAdmin):
    list_display = ('employee', 'hourly_rate', 'start_date', 'end_date')
    list_filter = ('employee', 'start_date', 'end_date')
    search_fields = ('employee__name',)
    ordering = ('employee__id', '-start_date')