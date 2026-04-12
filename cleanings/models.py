from decimal import Decimal

from django.db import models
from cloudinary.models import CloudinaryField

from apartments.models import Apartment
from employees.models import Employee


class Cleaning(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Programmato"),
        ("completed", "Completato"),
    ]

    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name="cleanings",
        verbose_name="Immobile"
    )

    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cleanings",
        verbose_name="Prenotazione collegata"
    )

    date = models.DateField(verbose_name="Data")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled",
        verbose_name="Stato"
    )

    employees = models.ManyToManyField(
        Employee,
        blank=True,
        related_name="cleanings",
        verbose_name="Dipendenti"
    )

    employee_note = models.TextField(
        blank=True,
        verbose_name="Nota finale dipendente"
    )

    people_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Numero persone"
    )

    double_beds_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Letti matrimoniali utilizzati"
    )

    single_beds_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Letti singoli utilizzati"
    )

    cleaning_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo pulizia"
    )

    fixed_kit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo kit fisso"
    )

    per_person_kit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo kit a persona"
    )

    double_bed_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo letto matrimoniale"
    )

    single_bed_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo letto singolo"
    )

    mat_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Tappetino"
    )

    extra_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Extra"
    )

    auto_created = models.BooleanField(
        default=False,
        verbose_name="Creata automaticamente"
    )

    manual_date_override = models.BooleanField(
        default=False,
        verbose_name="Data modificata manualmente"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pulizia"
        verbose_name_plural = "Pulizie"
        ordering = ["date"]

    def __str__(self):
        return f"{self.apartment} - {self.date}"

    def load_booking_values(self):
        if not self.booking_id:
            self.people_count = 0
            self.double_beds_count = 0
            self.single_beds_count = 0
            return

        self.people_count = self.booking.people_count or 0
        self.double_beds_count = self.booking.double_beds or 0
        self.single_beds_count = self.booking.single_beds or 0

    def load_apartment_default_costs(self, force=False):
        if not self.apartment_id:
            return

        if force or self.cleaning_cost in [None, Decimal("0"), Decimal("0.00")]:
            self.cleaning_cost = self.apartment.default_cleaning_cost or Decimal("0.00")

        if force or self.fixed_kit_cost in [None, Decimal("0"), Decimal("0.00")]:
            self.fixed_kit_cost = self.apartment.default_fixed_kit_cost or Decimal("0.00")

        if force or self.per_person_kit_cost in [None, Decimal("0"), Decimal("0.00")]:
            self.per_person_kit_cost = self.apartment.default_per_person_kit_cost or Decimal("0.00")

        if force or self.double_bed_cost in [None, Decimal("0"), Decimal("0.00")]:
            self.double_bed_cost = self.apartment.default_double_bed_cost or Decimal("0.00")

        if force or self.single_bed_cost in [None, Decimal("0"), Decimal("0.00")]:
            self.single_bed_cost = self.apartment.default_single_bed_cost or Decimal("0.00")

        if force or self.mat_cost in [None, Decimal("0"), Decimal("0.00")]:
            self.mat_cost = self.apartment.default_mat_cost or Decimal("0.00")

        if force or self.extra_cost in [None, Decimal("0"), Decimal("0.00")]:
            self.extra_cost = self.apartment.default_extra_cost or Decimal("0.00")

    def apply_apartment_default_costs(self, force=True):
        self.load_booking_values()
        self.load_apartment_default_costs(force=force)

    def recalculate_from_sources(self, force_costs=False):
        self.load_booking_values()
        self.load_apartment_default_costs(force=force_costs)

    def save(self, *args, **kwargs):
        recalculate = kwargs.pop("recalculate", True)

        if recalculate:
            self.recalculate_from_sources(force_costs=False)

        super().save(*args, **kwargs)

    @property
    def total_cost(self):
        return (
            (self.cleaning_cost or Decimal("0.00")) +
            (self.fixed_kit_cost or Decimal("0.00")) +
            ((self.per_person_kit_cost or Decimal("0.00")) * Decimal(self.people_count or 0)) +
            ((self.double_bed_cost or Decimal("0.00")) * Decimal(self.double_beds_count or 0)) +
            ((self.single_bed_cost or Decimal("0.00")) * Decimal(self.single_beds_count or 0)) +
            (self.mat_cost or Decimal("0.00")) +
            (self.extra_cost or Decimal("0.00"))
        )


class CleaningAttachment(models.Model):
    cleaning = models.ForeignKey(
        Cleaning,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Pulizia"
    )

    file = CloudinaryField(
        resource_type="auto",
        folder="cleaning_boost/cleaning_attachments",
        verbose_name="File"
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nota"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Caricato il"
    )

    class Meta:
        verbose_name = "Allegato pulizia"
        verbose_name_plural = "Allegati pulizia"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Allegato #{self.id} - Pulizia {self.cleaning_id}"

    @property
    def filename(self):
        value = str(self.file)
        return value.split("/")[-1]