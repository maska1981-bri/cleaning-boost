from customers.models import Customer
from apartments.models import Apartment
from employees.models import Employee

# Pulisce dati vecchi demo (opzionale sicurezza)
Customer.objects.all().delete()
Apartment.objects.all().delete()
Employee.objects.all().delete()

# CLIENTI
c1 = Customer.objects.create(name="Mario Rossi")
c2 = Customer.objects.create(name="B&B Lago Blu")

# IMMOBILI
a1 = Apartment.objects.create(
    customer=c1,
    code="APT001",
    name="Casa Centro",
    address="Via Roma 10",
    max_guests=4,
)

a2 = Apartment.objects.create(
    customer=c2,
    code="APT002",
    name="Appartamento Lago",
    address="Via Lago 5",
    max_guests=6,
)

# DIPENDENTI
Employee.objects.create(name="Anna")
Employee.objects.create(name="Luca")
Employee.objects.create(name="Marco")

print("DATI DEMO CREATI")