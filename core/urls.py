from django.contrib import admin

admin.site.site_url = "/app/"

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import never_cache

from core.views import landing_page
from core.sitemaps import StaticViewSitemap

from operations_calendar.views import calendar_month_view, public_demo_calendar
from employees.views import custom_logout

sitemaps = {
    "static": StaticViewSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "login/",
        never_cache(
            auth_views.LoginView.as_view(
                template_name="registration/login.html",
                redirect_authenticated_user=False,
            )
        ),
        name="login",
    ),
    path("logout/", custom_logout, name="logout"),
    path("", include("employees.urls")),
    path("", landing_page, name="landing"),
    path("app/", calendar_month_view, name="calendar"),
    path("demo/", public_demo_calendar),
    path("", include("operations_calendar.urls")),
    path("", include("condominiums.urls")),
    path("", include("cleanings.urls")),
    path("", include("accounting.urls")),
    path("employee-hours/", include("employee_hours.urls")),
    path("laundry/", include("laundry.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
