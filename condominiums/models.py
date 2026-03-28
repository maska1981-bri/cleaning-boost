from django.db import models
from apartments.models import Apartment


class CondominiumCleaningRule(models.Model):

    FREQUENCY_CHOICES = [
        ("daily", "Giornaliera"),
        ("twice_week", "2 volte settimana"),
        ("weekly", "Settimanale"),
        ("biweekly", "Quindicinale"),
        ("monthly", "Mensile"),
    ]

    WEEKDAY_CHOICES = [
        (0, "Lunedì"),
        (1, "Martedì"),
        (2, "Mercoledì"),
        (3, "Giovedì"),
        (4, "Venerdì"),
        (5, "Sabato"),
        (6, "Domenica"),
    ]

    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name="condominium_rules",
        verbose_name="Condominio"
    )

    start_date = models.DateField("Data inizio")
    end_date = models.DateField("Data fine", blank=True, null=True)

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        verbose_name="Frequenza"
    )

    preferred_day_1 = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        blank=True,
        null=True,
        verbose_name="Giorno preferito 1"
    )

    preferred_day_2 = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        blank=True,
        null=True,
        verbose_name="Giorno preferito 2"
    )

    work_hours = models.FloatField(
        verbose_name="Ore lavoro (1 persona)"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Note"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Regola pulizia condominio"
        verbose_name_plural = "Regole pulizia condomini"
        ordering = ["apartment", "start_date"]

    def __str__(self):
        return f"{self.apartment} - {self.frequency}"