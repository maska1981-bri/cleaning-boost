from decimal import Decimal
from io import BytesIO
from datetime import datetime, date
import zipfile
import csv
from tempfile import NamedTemporaryFile

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from cleanings.models import Cleaning
from customers.models import Customer


def dashboard_view(request):
    today = date.today()

    month_start = date(today.year, today.month, 1)

    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
    else:
        next_month_start = date(today.year, today.month + 1, 1)

    year_start = date(today.year, 1, 1)
    next_year_start = date(today.year + 1, 1, 1)

    cleanings_month = Cleaning.objects.filter(
        date__gte=month_start,
        date__lt=next_month_start
    ).select_related("apartment", "apartment__customer")

    cleanings_year = Cleaning.objects.filter(
        date__gte=year_start,
        date__lt=next_year_start
    ).select_related("apartment", "apartment__customer")

    month_total = Decimal("0.00")
    year_total = Decimal("0.00")
    count = 0

    customer_totals = {}

    for cleaning in cleanings_month:
        cost = cleaning.total_cost
        month_total += cost
        count += 1

        customer = cleaning.apartment.customer
        if not customer:
            continue

        if customer.id not in customer_totals:
            customer_totals[customer.id] = {
                "customer": customer,
                "total": Decimal("0.00"),
                "count": 0,
            }

        customer_totals[customer.id]["total"] += cost
        customer_totals[customer.id]["count"] += 1

    for cleaning in cleanings_year:
        year_total += cleaning.total_cost

    average = Decimal("0.00")
    if count > 0:
        average = (month_total / count).quantize(Decimal("0.01"))

    top_customers = sorted(
        customer_totals.values(),
        key=lambda x: x["total"],
        reverse=True
    )[:10]

    return render(request, "accounting/dashboard.html", {
        "month_total": month_total.quantize(Decimal("0.01")),
        "year_total": year_total.quantize(Decimal("0.01")),
        "monthly_cleanings_count": count,
        "average_per_cleaning": average,
        "top_customers": top_customers,
    })


def accounting_report(request):
    customers = Customer.objects.filter(is_active=True).order_by("name")

    customer_id = request.GET.get("customer")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    vat_raw = request.GET.get("vat_percentage", "22")

    try:
        vat_percentage = Decimal(vat_raw or "22")
    except Exception:
        vat_percentage = Decimal("22")

    selected_customer = None
    rows = []
    subtotal = Decimal("0.00")
    vat_amount = Decimal("0.00")
    total_with_vat = Decimal("0.00")

    if customer_id:
        selected_customer = get_object_or_404(Customer, id=customer_id, is_active=True)

    if selected_customer and date_from and date_to:
        cleanings = (
            Cleaning.objects
            .filter(
                apartment__customer=selected_customer,
                date__gte=date_from,
                date__lte=date_to,
            )
            .select_related("apartment", "booking")
            .prefetch_related("employees")
            .order_by("date", "apartment__name")
        )

        for cleaning in cleanings:
            cleaning_cost = cleaning.cleaning_cost or Decimal("0.00")
            fixed_kit_cost = cleaning.fixed_kit_cost or Decimal("0.00")
            per_person_kit_cost = cleaning.per_person_kit_cost or Decimal("0.00")
            double_bed_cost = cleaning.double_bed_cost or Decimal("0.00")
            single_bed_cost = cleaning.single_bed_cost or Decimal("0.00")
            mat_cost = cleaning.mat_cost or Decimal("0.00")
            extra_cost = cleaning.extra_cost or Decimal("0.00")
            people_count = cleaning.people_count or 0
            double_beds_count = cleaning.double_beds_count or 0
            single_beds_count = cleaning.single_beds_count or 0
            total_cost = cleaning.total_cost or Decimal("0.00")

            subtotal += total_cost

            rows.append({
                "booking": cleaning.booking,
                "apartment": cleaning.apartment,
                "cleaning": cleaning,
                "cleaning_cost": cleaning_cost,
                "fixed_kit_cost": fixed_kit_cost,
                "per_person_kit_cost": per_person_kit_cost,
                "double_bed_cost": double_bed_cost,
                "single_bed_cost": single_bed_cost,
                "mat_cost": mat_cost,
                "extra_cost": extra_cost,
                "people_count": people_count,
                "double_beds_count": double_beds_count,
                "single_beds_count": single_beds_count,
                "total_cost": total_cost,
            })

        vat_amount = (subtotal * vat_percentage / Decimal("100")).quantize(Decimal("0.01"))
        total_with_vat = (subtotal + vat_amount).quantize(Decimal("0.01"))

    return render(request, "accounting/report.html", {
        "customers": customers,
        "selected_customer": selected_customer,
        "date_from": date_from,
        "date_to": date_to,
        "vat_percentage": vat_percentage,
        "rows": rows,
        "subtotal": subtotal.quantize(Decimal("0.01")),
        "vat_amount": vat_amount,
        "total_with_vat": total_with_vat,
    })


def accounting_pdf(request):
    customer_id = request.GET.get("customer")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    vat_raw = request.GET.get("vat_percentage", "22")

    try:
        vat_percentage = Decimal(vat_raw or "22")
    except Exception:
        vat_percentage = Decimal("22")

    customer = get_object_or_404(Customer, id=customer_id, is_active=True)

    cleanings = (
        Cleaning.objects
        .filter(
            apartment__customer=customer,
            date__gte=date_from,
            date__lte=date_to,
        )
        .select_related("apartment", "booking")
        .order_by("date", "apartment__name")
    )

    subtotal = Decimal("0.00")
    rows = []

    for cleaning in cleanings:
        total_cost = cleaning.total_cost or Decimal("0.00")
        subtotal += total_cost

        rows.append({
            "cleaning": cleaning,
            "apartment_name": cleaning.apartment.name,
            "date": cleaning.date,
            "booking_label": f"Booking #{cleaning.booking.id}" if cleaning.booking else "Pulizia manuale",
            "guest_name": cleaning.booking.guest_name if cleaning.booking and cleaning.booking.guest_name else "-",
            "people_count": cleaning.people_count or 0,
            "double_beds_count": cleaning.double_beds_count or 0,
            "single_beds_count": cleaning.single_beds_count or 0,
            "cleaning_cost": cleaning.cleaning_cost or Decimal("0.00"),
            "fixed_kit_cost": cleaning.fixed_kit_cost or Decimal("0.00"),
            "per_person_kit_cost": cleaning.per_person_kit_cost or Decimal("0.00"),
            "double_bed_cost": cleaning.double_bed_cost or Decimal("0.00"),
            "single_bed_cost": cleaning.single_bed_cost or Decimal("0.00"),
            "mat_cost": cleaning.mat_cost or Decimal("0.00"),
            "extra_cost": cleaning.extra_cost or Decimal("0.00"),
            "total_cost": total_cost,
        })

    vat = (subtotal * vat_percentage / Decimal("100")).quantize(Decimal("0.01"))
    total = (subtotal + vat).quantize(Decimal("0.01"))

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left = 40
    right = width - 40
    y = height - 40

    def ensure_space(current_y, needed=80):
        nonlocal p, y
        if current_y < needed:
            p.showPage()
            y = height - 40
            draw_header()

    def money(value):
        return f"EUR {Decimal(value).quantize(Decimal('0.01'))}"

    def draw_header():
        nonlocal y
        p.setFont("Helvetica-Bold", 16)
        p.drawString(left, y, "Report servizi")

        y -= 24
        p.setFont("Helvetica", 10)
        p.drawString(left, y, f"Cliente: {customer.name}")

        y -= 16
        p.drawString(left, y, f"Periodo: {date_from} - {date_to}")

        y -= 16
        p.drawString(left, y, f"IVA: {vat_percentage}%")

        y -= 18
        p.line(left, y, right, y)
        y -= 18

    draw_header()

    for row in rows:
        ensure_space(y, 140)

        p.setFont("Helvetica-Bold", 11)
        p.drawString(left, y, row["apartment_name"])

        y -= 14
        p.setFont("Helvetica", 10)
        p.drawString(left, y, f"Data pulizia: {row['date']}")
        p.drawString(250, y, row["booking_label"])

        y -= 14
        p.drawString(left, y, f"Ospite: {row['guest_name']}")

        y -= 14
        p.drawString(
            left,
            y,
            f"Persone: {row['people_count']}   Matrimoniali: {row['double_beds_count']}   Singoli: {row['single_beds_count']}"
        )

        y -= 18
        p.setFont("Helvetica", 9)
        p.drawString(left + 10, y, f"Pulizia base: {money(row['cleaning_cost'])}")

        y -= 12
        p.drawString(left + 10, y, f"Kit fisso: {money(row['fixed_kit_cost'])}")

        y -= 12
        p.drawString(
            left + 10,
            y,
            f"Kit persona: {money(row['per_person_kit_cost'])} x {row['people_count']}"
        )

        y -= 12
        p.drawString(
            left + 10,
            y,
            f"Letti matrimoniali: {money(row['double_bed_cost'])} x {row['double_beds_count']}"
        )

        y -= 12
        p.drawString(
            left + 10,
            y,
            f"Letti singoli: {money(row['single_bed_cost'])} x {row['single_beds_count']}"
        )

        y -= 12
        p.drawString(left + 10, y, f"Tappetino: {money(row['mat_cost'])}")

        y -= 12
        p.drawString(left + 10, y, f"Extra: {money(row['extra_cost'])}")

        y -= 16
        p.setFont("Helvetica-Bold", 10)
        p.drawString(left + 10, y, f"Totale pulizia: {money(row['total_cost'])}")

        y -= 12
        p.line(left, y, right, y)
        y -= 18

    ensure_space(y, 80)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(left, y, f"Imponibile: {money(subtotal)}")

    y -= 16
    p.drawString(left, y, f"IVA {vat_percentage}%: {money(vat)}")

    y -= 16
    p.drawString(left, y, f"Totale: {money(total)}")

    p.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type="application/pdf")


def monthly_report(request):
    month = request.GET.get("month")
    year = request.GET.get("year")

    data = []

    if month and year:
        month_int = int(month)
        year_int = int(year)

        date_from = datetime(year_int, month_int, 1).date()

        if month_int == 12:
            date_to = datetime(year_int + 1, 1, 1).date()
        else:
            date_to = datetime(year_int, month_int + 1, 1).date()

        cleanings = Cleaning.objects.filter(
            date__gte=date_from,
            date__lt=date_to
        ).select_related("apartment", "apartment__customer")

        totals = {}

        for cleaning in cleanings:
            customer = cleaning.apartment.customer
            if not customer:
                continue

            if customer.id not in totals:
                totals[customer.id] = {
                    "customer": customer,
                    "total": Decimal("0.00"),
                }

            totals[customer.id]["total"] += cleaning.total_cost

        data = sorted(totals.values(), key=lambda x: x["customer"].name)

    return render(request, "accounting/monthly.html", {
        "data": data,
        "month": month,
        "year": year
    })


def monthly_invoices_zip(request):
    from accounting.models import Invoice

    month = int(request.GET.get("month"))
    year = int(request.GET.get("year"))
    vat_raw = request.GET.get("vat_percentage", "22")

    try:
        vat_percentage = Decimal(vat_raw or "22")
    except Exception:
        vat_percentage = Decimal("22")

    date_from = datetime(year, month, 1).date()

    if month == 12:
        date_to = datetime(year + 1, 1, 1).date()
    else:
        date_to = datetime(year, month + 1, 1).date()

    customers = Customer.objects.filter(is_active=True).order_by("name")

    temp_zip = NamedTemporaryFile(delete=False)
    zipf = zipfile.ZipFile(temp_zip.name, "w")

    for customer in customers:
        cleanings = (
            Cleaning.objects
            .filter(
                apartment__customer=customer,
                date__gte=date_from,
                date__lt=date_to,
            )
            .select_related("apartment", "booking")
            .order_by("date", "apartment__name")
        )

        subtotal = Decimal("0.00")
        rows = []

        for cleaning in cleanings:
            cost = cleaning.total_cost or Decimal("0.00")

            if cost > 0:
                subtotal += cost
                rows.append((cleaning, cost))

        if subtotal == 0:
            continue

        last_invoice = Invoice.objects.filter(year=year).order_by("-number").first()
        next_number = 1 if not last_invoice else last_invoice.number + 1

        invoice = Invoice.objects.create(
            customer=customer,
            year=year,
            number=next_number
        )

        vat = (subtotal * vat_percentage / Decimal("100")).quantize(Decimal("0.01"))
        total = (subtotal + vat).quantize(Decimal("0.01"))

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        y = 800

        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, f"Fattura n. {invoice.number}/{invoice.year}")

        y -= 25
        p.setFont("Helvetica", 11)
        p.drawString(50, y, f"Cliente: {customer.name}")

        y -= 20
        p.drawString(50, y, f"Periodo: {month}/{year}")

        y -= 30

        for cleaning, cost in rows:
            if cleaning.booking:
                text = (
                    f"{cleaning.apartment.name} | "
                    f"{cleaning.date} | "
                    f"Booking #{cleaning.booking.id} | "
                    f"EUR {cost}"
                )
            else:
                text = f"{cleaning.apartment.name} | {cleaning.date} | Pulizia manuale | EUR {cost}"

            p.drawString(50, y, text)
            y -= 18

            if y < 100:
                p.showPage()
                y = 800

        y -= 20
        p.drawString(50, y, f"Imponibile: EUR {subtotal}")

        y -= 20
        p.drawString(50, y, f"IVA {vat_percentage}%: EUR {vat}")

        y -= 20
        p.drawString(50, y, f"Totale: EUR {total}")

        p.save()
        buffer.seek(0)

        safe_name = customer.name.replace(" ", "_").replace("/", "_")
        filename = f"Fattura_{invoice.number}_{invoice.year}_{safe_name}.pdf"
        zipf.writestr(filename, buffer.read())

    zipf.close()

    return FileResponse(open(temp_zip.name, "rb"), as_attachment=True, filename="fatture.zip")


def export_excel(request):
    customer_id = request.GET.get("customer")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    customer = Customer.objects.get(id=customer_id)

    cleanings = (
        Cleaning.objects
        .filter(
            apartment__customer=customer,
            date__gte=date_from,
            date__lte=date_to,
        )
        .select_related("apartment", "booking")
        .order_by("date", "apartment__name")
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=report_contabilita.csv"

    writer = csv.writer(response)
    writer.writerow([
        "Immobile",
        "Data pulizia",
        "Prenotazione",
        "Ospite",
        "Totale"
    ])

    for cleaning in cleanings:
        writer.writerow([
            cleaning.apartment.name,
            cleaning.date,
            cleaning.booking.id if cleaning.booking else "",
            cleaning.booking.guest_name if cleaning.booking else "Pulizia manuale",
            cleaning.total_cost
        ])

    return response