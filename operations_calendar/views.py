from datetime import date, timedelta, datetime
import json
import calendar
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apartments.models import Apartment
from bookings.models import Booking
from cleanings.models import Cleaning, CleaningAttachment
from employees.models import Employee
from operations_calendar.models import DayNote


MONTHS_IT = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
}


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


def get_request_employee(request):
    if not request.user.is_authenticated:
        return None

    if request.user.is_staff or request.user.is_superuser:
        return None

    employee = getattr(request.user, "employee_profile", None)

    if employee and employee.is_active:
        return employee

    return None


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


@staff_required
def calendar_month_view(request):
    today = date.today()

    view_mode = request.GET.get("view", "compact")
    property_type = request.GET.get("type")
    anchor_str = request.GET.get("start")
    sort_mode = request.GET.get("sort", "code")

    if anchor_str:
        try:
            anchor_date = datetime.strptime(anchor_str, "%Y-%m-%d").date()
        except ValueError:
            anchor_date = today
    else:
        anchor_date = today

    if view_mode == "week":
        start_date = anchor_date - timedelta(days=anchor_date.weekday())
        end_date = start_date + timedelta(days=6)
        prev_start = start_date - timedelta(days=7)
        next_start = start_date + timedelta(days=7)
        buffer_before = 3
        buffer_after = 3

    elif view_mode == "15days":
        start_date = anchor_date
        end_date = start_date + timedelta(days=14)
        prev_start = start_date - timedelta(days=15)
        next_start = start_date + timedelta(days=15)
        buffer_before = 7
        buffer_after = 7

    elif view_mode == "quarter":
        start_date = anchor_date
        end_date = start_date + timedelta(days=89)
        prev_start = start_date - timedelta(days=90)
        next_start = start_date + timedelta(days=90)
        buffer_before = 30
        buffer_after = 30

    elif view_mode == "compact":
        start_date = anchor_date
        end_date = start_date + timedelta(days=13)
        prev_start = start_date - timedelta(days=14)
        next_start = start_date + timedelta(days=14)
        buffer_before = 10
        buffer_after = 10

    else:
        view_mode = "month"
        start_date = anchor_date.replace(day=1)

        if start_date.month == 12:
            next_month = date(start_date.year + 1, 1, 1)
        else:
            next_month = date(start_date.year, start_date.month + 1, 1)

        end_date = next_month - timedelta(days=1)
        prev_start = add_months(start_date, -1).replace(day=1)
        next_start = add_months(start_date, 1).replace(day=1)
        buffer_before = 7
        buffer_after = 7

    display_start = start_date - timedelta(days=buffer_before)
    display_end = end_date + timedelta(days=buffer_after)

    days = []
    current = display_start
    while current <= display_end:
        days.append(current)
        current += timedelta(days=1)

    month_groups = []
    current_month_label = None
    current_count = 0

    for day in days:
        label = f"{MONTHS_IT[day.month]} {day.year}"

        if label != current_month_label:
            if current_month_label is not None:
                month_groups.append({
                    "label": current_month_label,
                    "count": current_count,
                })
            current_month_label = label
            current_count = 1
        else:
            current_count += 1

    if current_month_label is not None:
        month_groups.append({
            "label": current_month_label,
            "count": current_count,
        })

    apartments = Apartment.objects.filter(is_active=True)

    if property_type:
        apartments = apartments.filter(property_type=property_type)

    apartments = apartments.order_by("code")

    bookings = Booking.objects.filter(
        apartment__is_active=True,
        check_in__lte=display_end,
        check_out__gte=display_start,
    ).select_related("apartment")

    if property_type:
        bookings = bookings.filter(apartment__property_type=property_type)

    cleanings = Cleaning.objects.filter(
        apartment__is_active=True,
        date__range=[display_start, display_end],
    ).prefetch_related("employees", "apartment")

    if property_type:
        cleanings = cleanings.filter(apartment__property_type=property_type)

    day_notes = DayNote.objects.filter(
        apartment__is_active=True,
        date__range=[display_start, display_end],
    ).select_related("apartment")

    if property_type:
        day_notes = day_notes.filter(apartment__property_type=property_type)

    employees = Employee.objects.filter(is_active=True).order_by("name")

    booking_map = {}
    booking_checkin_map = {}
    booking_checkout_map = {}

    for booking in bookings:
        current_day = booking.check_in
        while current_day <= booking.check_out:
            key = (booking.apartment_id, current_day)

            if key not in booking_map:
                booking_map[key] = []

            booking_map[key].append(booking)
            current_day += timedelta(days=1)

        checkin_key = (booking.apartment_id, booking.check_in)
        if checkin_key not in booking_checkin_map:
            booking_checkin_map[checkin_key] = []
        booking_checkin_map[checkin_key].append(booking)

        checkout_key = (booking.apartment_id, booking.check_out)
        if checkout_key not in booking_checkout_map:
            booking_checkout_map[checkout_key] = []
        booking_checkout_map[checkout_key].append(booking)

    cleaning_map = {}
    for cleaning in cleanings:
        cleaning_map[(cleaning.apartment_id, cleaning.date)] = cleaning

    day_note_map = {}
    for note in day_notes:
        key = (note.apartment_id, note.date)
        if key not in day_note_map:
            day_note_map[key] = []
        day_note_map[key].append(note)

    apartment_rows = []

    for apartment in apartments:
        row_cells = []

        for day in days:
            key = (apartment.id, day)

            bookings_for_day = booking_map.get(key, [])
            booking = bookings_for_day[0] if bookings_for_day else None

            cleaning = cleaning_map.get(key)
            notes_for_day = day_note_map.get(key, [])

            is_check_in = key in booking_checkin_map
            is_check_out = key in booking_checkout_map

            show_booking_summary = False
            booking_summary = ""

            if booking:
                if booking.check_in == booking.check_out:
                    show_booking_summary = day == booking.check_in
                else:
                    show_booking_summary = day == (booking.check_in + timedelta(days=1))

                booking_summary = booking.stay_summary

            visible_note_text = ""
            for note in notes_for_day:
                if note.note_type == "VISIBLE" and note.notes:
                    visible_note_text = note.notes
                    break

            row_cells.append({
                "day": day,
                "booking": booking,
                "cleaning": cleaning,
                "day_notes": notes_for_day,
                "visible_note_text": visible_note_text,
                "is_check_in": is_check_in,
                "is_check_out": is_check_out,
                "show_booking_summary": show_booking_summary,
                "booking_summary": booking_summary,
            })

        has_relevant_day = False
        first_relevant_day = date.max

        for cell in row_cells:
            if cell["day"] < today:
                continue

            if cell["cleaning"] or cell["day_notes"]:
                has_relevant_day = True
                first_relevant_day = cell["day"]
                break

        apartment_rows.append({
            "apartment": apartment,
            "cells": row_cells,
            "has_relevant_day": has_relevant_day,
            "first_relevant_day": first_relevant_day,
        })

    if sort_mode == "activity":
        apartment_rows.sort(
            key=lambda row: (
                not row["has_relevant_day"],
                row["first_relevant_day"],
                row["apartment"].code,
            )
        )
    else:
        apartment_rows.sort(
            key=lambda row: row["apartment"].code
        )

    context = {
        "days": days,
        "month_groups": month_groups,
        "apartment_rows": apartment_rows,
        "employees": employees,
        "selected_type": property_type or "",
        "context_view": view_mode,
        "sort_mode": sort_mode,
        "is_compact_view": view_mode == "compact",
        "today": today,
        "start_date": start_date,
        "end_date": end_date,
        "prev_start": prev_start,
        "next_start": next_start,
    }

    return render(
        request,
        "operations_calendar/month_calendar.html",
        context,
    )

def public_demo_calendar(request):
    return calendar_month_view(request)


@csrf_exempt
@require_POST
@staff_required
def move_cleaning(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        cleaning_id = data.get("cleaning_id")
        new_date = data.get("date")

        if not cleaning_id or not new_date:
            return JsonResponse(
                {"status": "error", "message": "Dati mancanti"},
                status=400,
            )

        cleaning = get_object_or_404(Cleaning, id=cleaning_id)
        cleaning.date = datetime.strptime(new_date, "%Y-%m-%d").date()
        cleaning.manual_date_override = True
        cleaning.save()

        return JsonResponse({
            "status": "ok",
            "cleaning_id": cleaning.id,
            "new_date": cleaning.date.isoformat(),
        })

    except ValueError:
        return JsonResponse(
            {"status": "error", "message": "Formato data non valido"},
            status=400,
        )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500,
        )


@csrf_exempt
@require_POST
@staff_required
def create_day_note(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        apartment_id = data.get("apartment_id")
        date_value = data.get("date")
        note_type = data.get("note_type")
        note_text = (data.get("notes") or "").strip()

        if not apartment_id or not date_value or not note_type:
            return JsonResponse(
                {"status": "error", "message": "Dati mancanti"},
                status=400,
            )

        if note_type in ["CUSTOM", "VISIBLE"] and not note_text:
            return JsonResponse(
                {"status": "error", "message": "Testo nota mancante"},
                status=400,
            )

        apartment = get_object_or_404(Apartment, id=apartment_id)
        note_date = datetime.strptime(date_value, "%Y-%m-%d").date()

        if note_type in ["CUSTOM", "VISIBLE"]:
            note, created = DayNote.objects.update_or_create(
                apartment=apartment,
                date=note_date,
                note_type=note_type,
                defaults={"notes": note_text},
            )
        else:
            note, created = DayNote.objects.get_or_create(
                apartment=apartment,
                date=note_date,
                note_type=note_type,
            )

        return JsonResponse({
            "status": "ok",
            "created": created,
            "note_id": note.id,
            "short_label": note.short_label,
            "notes": note.notes,
        })

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500,
        )

@csrf_exempt
@require_POST
@staff_required
def delete_booking(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        booking_id = data.get("booking_id")

        if not booking_id:
            return JsonResponse(
                {"status": "error", "message": "Prenotazione non trovata in questa cella"},
                status=400,
            )

        booking = get_object_or_404(Booking, id=booking_id)
        booking.delete()

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500,
        )


@csrf_exempt
@require_POST
@staff_required
def delete_cleaning(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        cleaning_id = data.get("cleaning_id")

        if not cleaning_id:
            return JsonResponse(
                {"status": "error", "message": "Pulizia non trovata in questa cella"},
                status=400,
            )

        cleaning = get_object_or_404(Cleaning, id=cleaning_id)
        cleaning.delete()

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500,
        )


@csrf_exempt
@require_POST
@staff_required
def delete_day_notes(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        apartment_id = data.get("apartment_id")
        date_value = data.get("date")

        if not apartment_id or not date_value:
            return JsonResponse(
                {"status": "error", "message": "Dati mancanti"},
                status=400,
            )

        apartment = get_object_or_404(Apartment, id=apartment_id)
        note_date = datetime.strptime(date_value, "%Y-%m-%d").date()

        deleted_count, _ = DayNote.objects.filter(
            apartment=apartment,
            date=note_date,
        ).delete()

        if deleted_count == 0:
            return JsonResponse(
                {"status": "error", "message": "Nessuna nota trovata in questa cella"},
                status=400,
            )

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500,
        )


@csrf_exempt
@login_required
@require_POST
def update_cleaning_status(request):
    user = request.user
    is_admin_user = user.is_staff or user.is_superuser
    employee = get_request_employee(request)

    try:
        is_json_request = request.content_type == "application/json"

        if is_json_request:
            payload = json.loads(request.body)
            cleaning_id = payload.get("cleaning_id")
            status_value = payload.get("status")
        else:
            cleaning_id = request.POST.get("cleaning_id")
            status_value = request.POST.get("status")

        cleaning = Cleaning.objects.get(id=cleaning_id)

        # 🔒 PERMESSI
        if not is_admin_user:
            if not employee or not cleaning.employees.filter(id=employee.id).exists():
                raise PermissionDenied

        cleaning.status = status_value
        cleaning.save()

        if status_value == "completed":
            try:
                send_mail(
                    subject=f"Pulizia completata - {cleaning.apartment.name}",
                    message=(
                        f"La pulizia è stata completata.\n\n"
                        f"Immobile: {cleaning.apartment.name}\n"
                        f"Data: {cleaning.date}\n"
                        f"ID pulizia: {cleaning.id}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CLEANING_NOTIFICATION_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

        if is_json_request:
            return JsonResponse({"status": "ok"})

        return redirect("/employee-calendar/")

    except Cleaning.DoesNotExist:
        if request.content_type == "application/json":
            return JsonResponse(
                {"status": "error", "message": "Pulizia non trovata"},
                status=404
            )
        return redirect("/employee-calendar/")

    except PermissionDenied:
        if request.content_type == "application/json":
            return JsonResponse(
                {"status": "error", "message": "Permesso negato"},
                status=403
            )
        return redirect("/employee-calendar/")

    except Exception as e:
        if request.content_type == "application/json":
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=400
            )
        return redirect("/employee-calendar/")


@csrf_exempt
@require_POST
@staff_required
def toggle_cleaning_employee(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        cleaning_id = data.get("cleaning_id")
        employee_id = data.get("employee_id")

        if not cleaning_id or not employee_id:
            return JsonResponse(
                {"status": "error", "message": "Dati mancanti"},
                status=400,
            )

        cleaning = get_object_or_404(Cleaning, id=cleaning_id)
        employee = get_object_or_404(Employee, id=employee_id)

        if cleaning.employees.filter(id=employee.id).exists():
            cleaning.employees.remove(employee)
            assigned = False
        else:
            cleaning.employees.add(employee)
            assigned = True

        return JsonResponse({
            "status": "ok",
            "assigned": assigned,
            "employee_name": employee.name,
        })

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500,
        )


@login_required
def employee_calendar(request):
    today = now().date()
    start_str = request.GET.get("start")

    if start_str:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    else:
        start_date = today

    days = [start_date + timedelta(days=i) for i in range(7)]
    end_date = days[-1]

    is_admin_user = request.user.is_staff or request.user.is_superuser
    current_employee = get_request_employee(request)

    if not is_admin_user and current_employee is None:
        raise PermissionDenied

    apartments = Apartment.objects.filter(is_active=True).order_by("code")

    # 🔴 NOTE
    day_notes = DayNote.objects.filter(
        apartment__in=apartments,
        date__range=[start_date, end_date],
    ).select_related("apartment")

    day_note_map = {}
    for note in day_notes:
        key = (note.apartment_id, note.date)
        day_note_map.setdefault(key, []).append(note)

    apartment_rows = []

    for apartment in apartments:
        cells = []
        has_relevant_day = False
        first_relevant_day = None

        for day in days:
            booking = Booking.objects.filter(
                apartment=apartment,
                check_in__lte=day,
                check_out__gte=day
            ).first()

            notes_for_day = day_note_map.get((apartment.id, day), [])

            cleaning_qs = Cleaning.objects.filter(
                apartment=apartment,
                date=day
            ).prefetch_related("employees")

            if not is_admin_user:
                cleaning_qs = cleaning_qs.filter(employees=current_employee)

            cleaning = cleaning_qs.first()

            # 🔴 LOGICA ORDINAMENTO
            if (cleaning or notes_for_day) and not has_relevant_day:
                has_relevant_day = True
                first_relevant_day = day

            is_check_in = bool(booking and booking.check_in == day)
            is_check_out = bool(booking and booking.check_out == day)

            show_booking_summary = False
            booking_summary = ""

            if booking:
                if booking.check_in == booking.check_out:
                    show_booking_summary = day == booking.check_in
                else:
                    show_booking_summary = day == (booking.check_in + timedelta(days=1))

                parts = []
                if booking.people_count:
                    parts.append(f"{booking.people_count}p")
                if booking.double_beds:
                    parts.append(f"{booking.double_beds}M")
                if booking.single_beds:
                    parts.append(f"{booking.single_beds}S")
                booking_summary = " ".join(parts)

            cells.append({
                "day": day,
                "booking": booking,
                "cleaning": cleaning,
                "is_check_in": is_check_in,
                "is_check_out": is_check_out,
                "show_booking_summary": show_booking_summary,
                "booking_summary": booking_summary,
                "day_notes": notes_for_day,
            })

        apartment_rows.append({
            "apartment": apartment,
            "cells": cells,
            "has_relevant_day": has_relevant_day,
            "first_relevant_day": first_relevant_day or date.max,
        })

    # 🔴 ORDINAMENTO
    apartment_rows.sort(
        key=lambda x: (
            not x["has_relevant_day"],  # prima quelli con lavoro
            x["first_relevant_day"]     # poi per giorno
        )
    )

    context = {
        "today": today,
        "days": days,
        "apartment_rows": apartment_rows,
        "prev_start": start_date - timedelta(days=7),
        "next_start": start_date + timedelta(days=7),
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(
        request,
        "operations_calendar/employee_calendar.html",
        context
    )


@login_required
def employee_apartment_detail(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    is_admin_user = request.user.is_staff or request.user.is_superuser
    current_employee = get_request_employee(request)

    if not is_admin_user and current_employee is None:
        raise PermissionDenied

    photos = apartment.photos.all() if hasattr(apartment, "photos") else []

    context = {
        "apartment": apartment,
        "photos": photos,
    }

    return render(
        request,
        "operations_calendar/employee_apartment_detail.html",
        context
    )


@login_required
def employee_cleaning_detail(request, cleaning_id):
    cleaning = get_object_or_404(Cleaning, id=cleaning_id)
    apartment = cleaning.apartment
    booking = cleaning.booking

    is_admin_user = request.user.is_staff or request.user.is_superuser
    current_employee = get_request_employee(request)

    if not is_admin_user and current_employee is None:
        raise PermissionDenied

    if not is_admin_user and not cleaning.employees.filter(id=current_employee.id).exists():
        raise PermissionDenied

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "complete":
            cleaning.status = "completed"
            cleaning.employee_note = request.POST.get("employee_note", "")
            cleaning.save()

            try:
                send_mail(
                    subject=f"Pulizia completata - {cleaning.apartment.name}",
                    message=(
                        f"La pulizia è stata completata.\n\n"
                        f"Immobile: {cleaning.apartment.name}\n"
                        f"Data: {cleaning.date}\n"
                        f"ID pulizia: {cleaning.id}\n"
                        f"Dipendente: {current_employee.name if current_employee else request.user.username}\n\n"
                        f"Nota finale:\n{cleaning.employee_note or '-'}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CLEANING_NOTIFICATION_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

            return redirect("/employee-calendar/")

        if action == "upload":
            uploaded_file = request.FILES.get("attachment_file")
            note = request.POST.get("attachment_note", "").strip()

            if uploaded_file:
                CleaningAttachment.objects.create(
                    cleaning=cleaning,
                    file=uploaded_file,
                    note=note
                )
            return redirect(f"/employee-cleaning/{cleaning.id}/")

    attachments = cleaning.attachments.all() if hasattr(cleaning, "attachments") else []

    context = {
        "cleaning": cleaning,
        "apartment": apartment,
        "booking": booking,
        "attachments": attachments,
    }

    return render(
        request,
        "operations_calendar/employee_cleaning_detail.html",
        context
    )