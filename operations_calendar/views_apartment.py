from django.shortcuts import render, get_object_or_404
from apartments.models import Apartment


def apartment_detail(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    context = {
        "apartment": apartment
    }

    return render(
        request,
        "operations_calendar/apartment_detail.html",
        context
    )