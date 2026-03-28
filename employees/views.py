from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def post_login_redirect(request):
    user = request.user

    # ADMIN → homepage (dashboard principale)
    if user.is_staff or user.is_superuser:
        return redirect("calendar")

    # DIPENDENTE ATTIVO
    employee = getattr(user, "employee_profile", None)
    if employee and employee.is_active:
        return redirect("employee_calendar")

    # NON VALIDO → logout
    logout(request)
    return redirect("login")