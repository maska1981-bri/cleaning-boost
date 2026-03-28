from django.db import models
from apartments.models import Apartment


class Booking(models.Model):
    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Appartamento"
    )

    guest_name = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Nome ospite"
    )

    people_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Numero persone"
    )

    double_beds = models.PositiveIntegerField(
        default=0,
        verbose_name="Letti matrimoniali utilizzati"
    )

    single_beds = models.PositiveIntegerField(
        default=0,
        verbose_name="Letti singoli utilizzati"
    )

    check_in = models.DateField(
        verbose_name="Check-in"
    )

    check_in_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Ora check-in"
    )

    check_out = models.DateField(
        verbose_name="Check-out"
    )

    check_out_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Ora check-out"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Note"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["check_in"]
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"

    def __str__(self):
        return f"{self.apartment} {self.check_in} → {self.check_out}"

    @property
    def stay_summary(self):
        nights = (self.check_out - self.check_in).days
        return f"{nights}n"

    @property
    def beds_summary(self):
        parts = []

        if self.double_beds:
            parts.append(f"{self.double_beds}M")

        if self.single_beds:
            parts.append(f"{self.single_beds}S")

        return " ".join(parts)

    def sync_checkout_cleaning(self):
        from cleanings.models import Cleaning

        cleaning, created = Cleaning.objects.get_or_create(
            booking=self,
            defaults={
                "apartment": self.apartment,
                "date": self.check_out,
                "auto_created": True,
            }
        )

        cleaning.apartment = self.apartment

        if not cleaning.manual_date_override:
            cleaning.date = self.check_out

        cleaning.recalculate_from_sources(force_costs=True)
        cleaning.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_checkout_cleaning()

    def delete(self, *args, **kwargs):
        from cleanings.models import Cleaning
        Cleaning.objects.filter(booking=self, auto_created=True).delete()
        super().delete(*args, **kwargs)