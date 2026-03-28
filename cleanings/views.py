from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from .models import Cleaning


@require_http_methods(["GET", "POST"])
def cleaning_detail(request, cleaning_id):
    cleaning = get_object_or_404(
        Cleaning.objects.select_related("apartment", "booking").prefetch_related("employees"),
        id=cleaning_id
    )

    if request.method == "POST":
        cleaning.date = request.POST.get("date") or cleaning.date
        cleaning.cleaning_cost = request.POST.get("cleaning_cost") or Decimal("0.00")
        cleaning.fixed_kit_cost = request.POST.get("fixed_kit_cost") or Decimal("0.00")
        cleaning.per_person_kit_cost = request.POST.get("per_person_kit_cost") or Decimal("0.00")
        cleaning.double_bed_cost = request.POST.get("double_bed_cost") or Decimal("0.00")
        cleaning.single_bed_cost = request.POST.get("single_bed_cost") or Decimal("0.00")
        cleaning.mat_cost = request.POST.get("mat_cost") or Decimal("0.00")
        cleaning.extra_cost = request.POST.get("extra_cost") or Decimal("0.00")
        cleaning.people_count = request.POST.get("people_count") or 0
        cleaning.double_beds_count = request.POST.get("double_beds_count") or 0
        cleaning.single_beds_count = request.POST.get("single_beds_count") or 0
        cleaning.status = request.POST.get("status") or cleaning.status
        cleaning.employee_note = request.POST.get("employee_note", "")
        cleaning.manual_date_override = request.POST.get("manual_date_override") == "on"
        cleaning.save()

        return redirect("cleaning_detail", cleaning_id=cleaning.id)

    return render(
        request,
        "operations_calendar/cleaning_detail.html",
        {
            "cleaning": cleaning,
        },
    )