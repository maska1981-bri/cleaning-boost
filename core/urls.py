from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from operations_calendar.views import calendar_month_view

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/login/"),
        name="logout",
    ),

    path("", include("employees.urls")),
    path("", calendar_month_view, name="calendar"),
    path("", include("operations_calendar.urls")),
    path("", include("condominiums.urls")),
    path("", include("cleanings.urls")),
    path("", include("accounting.urls")),
    path("employee-hours/", include("employee_hours.urls")),
    path("laundry/", include("laundry.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)