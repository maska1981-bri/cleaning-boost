from django.db import models
from customers.models import Customer
from cloudinary.models import CloudinaryField


class Apartment(models.Model):

    PROPERTY_TYPES = [
        ("house", "Casa"),
        ("condo", "Condominio"),
        ("office", "Ufficio"),
        ("shop", "Locale"),
        ("other", "Altro"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="apartments",
        verbose_name="Cliente"
    )

    code = models.CharField(
        max_length=20,
        verbose_name="Codice"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nome"
    )

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default="house",
        verbose_name="Tipo immobile"
    )

    address = models.CharField(
        max_length=200,
        blank=True
    )

    max_guests = models.IntegerField(
        default=0
    )

    double_beds = models.IntegerField(
        default=0,
        verbose_name="Letti matrimoniali totali"
    )

    single_beds = models.IntegerField(
        default=0,
        verbose_name="Letti singoli totali"
    )

    google_maps_url = models.URLField(
        blank=True
    )

    operational_notes = models.TextField(
        blank=True
    )

    default_cleaning_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo pulizia"
    )

    default_fixed_kit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo kit fisso"
    )

    default_per_person_kit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo kit a persona"
    )

    default_double_bed_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo letto matrimoniale"
    )

    default_single_bed_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Costo letto singolo"
    )

    default_mat_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Tappetino"
    )

    default_extra_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Extra"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Immobile"
        verbose_name_plural = "Immobili"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"

class ApartmentPhoto(models.Model):
    apartment = models.ForeignKey("Apartment", on_delete=models.CASCADE, related_name="photos")
    image = CloudinaryField(
    resource_type="image",
    folder="cleaning_boost/apartment_photos",
    verbose_name="Foto"
)
    caption = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.apartment} - Foto"