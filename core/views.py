from django.shortcuts import render, redirect


def landing_page(request):
    if not request.user.is_authenticated:
        return render(request, "landing.html")

    if request.user.username == "demo":
        return redirect("/app/")

    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")

    employee = getattr(request.user, "employee_profile", None)

    if employee and employee.is_active:
        return redirect("/employee-calendar/")

    return redirect("/logout/")
