from django.db import models


INITIAL_LAUNDRY_ITEMS = [
    ("tappetino", "Tappetini"),
    ("telo_bagno", "Telo bagno"),
    ("telo_viso", "Telo viso"),
    ("telo_bidet", "Telo bidet"),
    ("lenzuolo_matrimoniale", "Lenzuolo matrimoniale"),
    ("lenzuolo_singolo", "Lenzuolo singolo"),
    ("copripiumino_matrimoniale", "Copripiumino matrimoniale"),
    ("copripiumino_singolo", "Copripiumino singolo"),
    ("federa", "Federe"),
]


class LaundryItem(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LaundryInventory(models.Model):
    item = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=0)

    class Meta:
        ordering = ["item"]

    def __str__(self):
        return f"{self.item} - {self.quantity}"


class LaundryMovement(models.Model):
    MOVEMENT_TYPE = [
        ("dirty", "Sporco"),
        ("clean", "Pulito"),
        ("add", "Integrazione"),
        ("remove", "Diminuzione"),
    ]

    date = models.DateField()
    item = models.CharField(max_length=100)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.date} - {self.item} - {self.quantity} - {self.movement_type}"