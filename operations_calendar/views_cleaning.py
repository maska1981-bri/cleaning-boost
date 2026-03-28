from decimal import Decimal, InvalidOperation

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from cleanings.models import Cleaning


@login_required
def cleaning_detail(request, cleaning_id):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied

    cleaning = get_object_or_404(
        Cleaning.objects.select_related("apartment", "booking").prefetch_related("employees", "attachments"),
        id=cleaning_id
    )

    if request.method == "POST":
        def to_decimal(value):
            value = (value or "").strip().replace(",", ".")
            if value == "":
                return Decimal("0.00")
            try:
                return Decimal(value)
            except (InvalidOperation, TypeError):
                return Decimal("0.00")

        cleaning.cleaning_cost = to_decimal(request.POST.get("cleaning_cost"))
        cleaning.fixed_kit_cost = to_decimal(request.POST.get("fixed_kit_cost"))
        cleaning.per_person_kit_cost = to_decimal(request.POST.get("per_person_kit_cost"))
        cleaning.double_bed_cost = to_decimal(request.POST.get("double_bed_cost"))
        cleaning.single_bed_cost = to_decimal(request.POST.get("single_bed_cost"))
        cleaning.mat_cost = to_decimal(request.POST.get("mat_cost"))
        cleaning.extra_cost = to_decimal(request.POST.get("extra_cost"))

        cleaning.save()
        return redirect(f"/cleaning/{cleaning.id}/")

    attachments = cleaning.attachments.all() if hasattr(cleaning, "attachments") else []

    context = {
        "cleaning": cleaning,
        "booking": cleaning.booking,
        "apartment": cleaning.apartment,
        "attachments": attachments,
    }

    return render(
        request,
        "operations_calendar/cleaning_detail.html",
        context
    )