from datetime import timedelta

from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from cleanings.models import Cleaning
from .models import CondominiumCleaningRule


def should_generate_for_day(rule, current_date):
    if current_date < rule.start_date:
        return False

    if rule.end_date and current_date > rule.end_date:
        return False

    frequency = rule.frequency
    weekday = current_date.weekday()

    if frequency == "daily":
        return True

    if frequency == "weekly":
        if rule.preferred_day_1 is None:
            return False
        return weekday == rule.preferred_day_1

    if frequency == "twice_week":
        valid_days = []
        if rule.preferred_day_1 is not None:
            valid_days.append(rule.preferred_day_1)
        if rule.preferred_day_2 is not None:
            valid_days.append(rule.preferred_day_2)
        return weekday in valid_days

    if frequency == "biweekly":
        if rule.preferred_day_1 is None:
            return False
        if weekday != rule.preferred_day_1:
            return False

        days_from_start = (current_date - rule.start_date).days
        weeks_from_start = days_from_start // 7
        return weeks_from_start % 2 == 0

    if frequency == "monthly":
        if rule.preferred_day_1 is None:
            return False
        if weekday != rule.preferred_day_1:
            return False

        return 1 <= current_date.day <= 7

    return False


@require_POST
def generate_condominium_cleanings(request):
    rules = CondominiumCleaningRule.objects.filter(is_active=True).select_related("apartment")

    created_count = 0

    for rule in rules:
        current_date = rule.start_date
        final_date = rule.end_date if rule.end_date else (rule.start_date + timedelta(days=365))

        while current_date <= final_date:
            if should_generate_for_day(rule, current_date):
                exists = Cleaning.objects.filter(
                    apartment=rule.apartment,
                    date=current_date,
                ).exists()

                if not exists:
                    Cleaning.objects.create(
                        apartment=rule.apartment,
                        date=current_date,
                        status="scheduled",
                        notes=f"Generata da regola condominio - {rule.get_frequency_display()}",
                    )
                    created_count += 1

            current_date += timedelta(days=1)

    messages.success(
        request,
        f"Generate {created_count} pulizie condominiali."
    )

    return redirect("/")