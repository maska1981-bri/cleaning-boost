from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
        verbose_name="Utente login",
    )
    name = models.CharField(max_length=100, verbose_name="Nome")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefono")
    email = models.EmailField(blank=True, verbose_name="Email")
    color = models.CharField(
        max_length=7,
        default="#3498db",
        verbose_name="Colore calendario"
    )
    is_active = models.BooleanField(default=True, verbose_name="Attivo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dipendente"
        verbose_name_plural = "Dipendenti"
        ordering = ["name"]

    @property
    def initials(self):
        parts = self.name.strip().split()

        if len(parts) == 0:
            return ""

        if len(parts) == 1:
            return parts[0][:2].upper()

        return (parts[0][0] + parts[-1][0]).upper()

    def __str__(self):
        return self.name