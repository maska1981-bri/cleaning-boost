from django.urls import path
from .views import (
    calendar_month_view,
    move_cleaning,
    create_day_note,
    delete_booking,
    delete_cleaning,
    delete_day_notes,
    update_cleaning_status,
    toggle_cleaning_employee,
    employee_calendar,
    employee_apartment_detail,
    employee_cleaning_detail,
)
from .views_apartment import apartment_detail
from .views_cleaning import cleaning_detail

urlpatterns = [
    path("old-calendar/", calendar_month_view, name="old_calendar"),
    path("move-cleaning/", move_cleaning, name="move_cleaning"),
    path("create-day-note/", create_day_note, name="create_day_note"),
    path("delete-booking/", delete_booking, name="delete_booking"),
    path("delete-cleaning/", delete_cleaning, name="delete_cleaning"),
    path("delete-day-notes/", delete_day_notes, name="delete_day_notes"),
    path("update-cleaning-status/", update_cleaning_status, name="update_cleaning_status"),
    path("toggle-cleaning-employee/", toggle_cleaning_employee, name="toggle_cleaning_employee"),
    path("apartment/<int:apartment_id>/", apartment_detail, name="apartment_detail"),
    path("cleaning/<int:cleaning_id>/", cleaning_detail, name="cleaning_detail"),
    path("employee-calendar/", employee_calendar, name="employee_calendar"),
    path("employee-apartment/<int:apartment_id>/", employee_apartment_detail, name="employee_apartment_detail"),
    path("employee-cleaning/<int:cleaning_id>/", employee_cleaning_detail, name="employee_cleaning_detail"),
]