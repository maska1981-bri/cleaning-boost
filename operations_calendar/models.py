from django.db import models
from apartments.models import Apartment


class DayNote(models.Model):
    NOTE_CHOICES = [
        ("PROP", "Prop"),
        ("CANE", "Cane"),
        ("SOLO_PULIZIA", "Solo pulizia"),
        ("NO_BIANCHERIA", "No biancheria"),
        ("TUTTI_LETTI", "Tutti i letti"),
    ]

    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name="day_notes",
        verbose_name="Appartamento"
    )
    date = models.DateField(verbose_name="Data")
    note_type = models.CharField(
        max_length=30,
        choices=NOTE_CHOICES,
        verbose_name="Tipo nota"
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nota aggiuntiva"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota giornaliera"
        verbose_name_plural = "Note giornaliere"
        ordering = ["date"]
        unique_together = ("apartment", "date", "note_type")

    def __str__(self):
        return f"{self.apartment} - {self.date} - {self.get_note_type_display()}"

    @property
    def short_label(self):
        labels = {
            "PROP": "Prop",
            "CANE": "Cane",
            "SOLO_PULIZIA": "Solo pul.",
            "NO_BIANCHERIA": "No bianch.",
            "TUTTI_LETTI": "Tutti letti",
        }
        return labels.get(self.note_type, self.get_note_type_display())