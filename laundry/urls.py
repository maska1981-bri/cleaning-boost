from django.urls import path
from .views import laundry_view

urlpatterns = [
    path('', laundry_view, name='laundry'),
]