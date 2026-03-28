from datetime import date
import calendar
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.db.models import Q

from employees.models import Employee
from .models import WorkLog, HourlyRate


def get_hourly_rate_for_day(employee, day):
    rate = HourlyRate.objects.filter(
        employee=employee,
        start_date__lte=day
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=day)
    ).order_by('-start_date').first()

    return rate.hourly_rate if rate else Decimal('0')


def get_month_range(year, month):
    last_day = calendar.monthrange(year, month)[1]
    start_day = date(year, month, 1)
    end_day = date(year, month, last_day)
    return start_day, end_day, last_day


def worklog_table(request):
    employees = Employee.objects.all().order_by('id')

    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))

    month_start, month_end, num_days = get_month_range(year, month)
    days = [date(year, month, d) for d in range(1, num_days + 1)]

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_hours':
            for emp in employees:
                for d in days:
                    day_str = d.strftime('%Y-%m-%d')
                    field_name = f"hours_{emp.id}_{day_str}"
                    raw_hours = request.POST.get(field_name, '').strip()

                    if raw_hours == '':
                        WorkLog.objects.filter(employee=emp, date=d).delete()
                        continue

                    raw_hours = raw_hours.replace(',', '.')

                    try:
                        hours_value = Decimal(raw_hours)
                    except (InvalidOperation, TypeError):
                        continue

                    obj, created = WorkLog.objects.get_or_create(
                        employee=emp,
                        date=d,
                        defaults={'hours': hours_value}
                    )

                    if not created:
                        obj.hours = hours_value
                        obj.save()

            return redirect(f'/employee-hours/?month={month}&year={year}')

        if action == 'save_rates':
            for emp in employees:
                field_name = f"rate_{emp.id}"
                raw_rate = request.POST.get(field_name, '').strip()

                if raw_rate == '':
                    continue

                raw_rate = raw_rate.replace(',', '.')

                try:
                    rate_value = Decimal(raw_rate)
                except (InvalidOperation, TypeError):
                    continue

                HourlyRate.objects.update_or_create(
                    employee=emp,
                    start_date=month_start,
                    end_date=month_end,
                    defaults={'hourly_rate': rate_value}
                )

            return redirect(f'/employee-hours/?month={month}&year={year}')

    logs = WorkLog.objects.filter(
        date__year=year,
        date__month=month
    ).select_related('employee')

    data = {}
    for log in logs:
        data[(log.employee_id, log.date)] = {'hours': log.hours}

    sidebar_data = []
    grand_total_hours = Decimal('0')
    grand_total_euro = Decimal('0')

    for emp in employees:
        total_hours = Decimal('0')

        for d in days:
            log = data.get((emp.id, d))
            if log:
                total_hours += log['hours']

        monthly_rate_obj = HourlyRate.objects.filter(
            employee=emp,
            start_date=month_start,
            end_date=month_end
        ).first()

        if monthly_rate_obj:
            hourly_rate = monthly_rate_obj.hourly_rate
        else:
            hourly_rate = Decimal('0')

        total_euro = total_hours * hourly_rate

        sidebar_data.append({
            'employee': emp,
            'total_hours': total_hours,
            'hourly_rate': hourly_rate,
            'total_euro': total_euro,
        })

        grand_total_hours += total_hours
        grand_total_euro += total_euro

    context = {
        'employees': employees,
        'days': days,
        'data': data,
        'sidebar_data': sidebar_data,
        'grand_total_hours': grand_total_hours,
        'grand_total_euro': grand_total_euro,
        'month': month,
        'year': year,
    }

    return render(request, 'employee_hours/worklog_table.html', context)