from django.contrib import admin
admin.site.site_url = "/app/"

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import landing_page

from operations_calendar.views import calendar_month_view
from employees.views import custom_logout
from operations_calendar.views import public_demo_calendar

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=False,
        ),
        name="login",
    ),
    path("logout/", custom_logout, name="logout"),

    path("", landing_page, name="landing"),
    path("app/", calendar_month_view, name="calendar"),
    path("demo/", public_demo_calendar),

    path("", include("operations_calendar.urls")),
    path("", include("condominiums.urls")),
    path("", include("cleanings.urls")),
    path("", include("accounting.urls")),
    path("employee-hours/", include("employee_hours.urls")),
    path("laundry/", include("laundry.urls")),

    path("employees/", include("employees.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)