from django.db import models


class Customer(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Nome cliente"
    )

    company_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Ragione sociale"
    )

    vat_number = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Partita IVA"
    )

    tax_code = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Codice fiscale"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )

    phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Telefono"
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Indirizzo"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Note"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Attivo"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"
        ordering = ["name"]

    def __str__(self):
        if self.company_name:
            return f"{self.name} - {self.company_name}"
        return self.name