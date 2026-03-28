from django.db import models
from employees.models import Employee


class HourlyRate(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['employee', '-start_date']

    def __str__(self):
        return f"{self.employee} - {self.hourly_rate} €/h"


class WorkLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['date', 'employee_id']

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.hours}"