from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def post_login_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")

    employee = getattr(request.user, "employee_profile", None)
    if employee and employee.is_active:
        return redirect("/employee-calendar/")

    logout(request)
    return redirect("/login/")


def custom_logout(request):
    request.session.flush()
    logout(request)
    response = redirect("/login/")
    response.delete_cookie("sessionid")
    response.delete_cookie("csrftoken")
    return response