from django.urls import path
from .views import worklog_table

urlpatterns = [
    path('', worklog_table, name='worklog'),
]