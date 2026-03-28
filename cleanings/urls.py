from django.urls import path
from .views import cleaning_detail

urlpatterns = [
    path("cleaning/<int:cleaning_id>/", cleaning_detail, name="cleaning_detail"),
]