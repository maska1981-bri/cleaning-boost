from django.db import models
from customers.models import Customer


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    year = models.IntegerField()
    number = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("year", "number")

    def __str__(self):
        return f"Fattura {self.number}/{self.year}"