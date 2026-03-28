from django.urls import path
from .views import dashboard_view, accounting_report, accounting_pdf, monthly_report, monthly_invoices_zip, export_excel

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard_view"),
    path("accounting/", accounting_report, name="accounting_report"),
    path("accounting/pdf/", accounting_pdf, name="accounting_pdf"),
    path("accounting/monthly/", monthly_report, name="monthly_report"),
    path("accounting/monthly-invoices/", monthly_invoices_zip, name="monthly_invoices_zip"),
    path("accounting/export/", export_excel, name="export_excel"),
]