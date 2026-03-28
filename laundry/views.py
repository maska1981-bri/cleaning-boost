from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.text import slugify

from .models import (
    LaundryItem,
    LaundryInventory,
    LaundryMovement,
    INITIAL_LAUNDRY_ITEMS,
)


def ensure_default_items():
    for code, name in INITIAL_LAUNDRY_ITEMS:
        LaundryItem.objects.get_or_create(
            code=code,
            defaults={"name": name, "active": True}
        )
        LaundryInventory.objects.get_or_create(item=code, defaults={"quantity": 0})


def laundry_view(request):
    ensure_default_items()

    if request.method == "POST":
        action = request.POST.get("action")

        # AGGIUNTA NUOVO ARTICOLO
        if action == "add_item":
            item_name = request.POST.get("item_name", "").strip()
            initial_quantity = request.POST.get("initial_quantity", "0").strip()

            if item_name == "":
                messages.error(request, "Inserisci il nome del nuovo articolo.")
                return redirect("/laundry/")

            code = slugify(item_name).replace("-", "_")

            if code == "":
                messages.error(request, "Nome articolo non valido.")
                return redirect("/laundry/")

            if LaundryItem.objects.filter(code=code).exists():
                messages.error(request, "Esiste già un articolo con questo nome.")
                return redirect("/laundry/")

            qty = int(initial_quantity) if initial_quantity else 0
            if qty < 0:
                qty = 0

            LaundryItem.objects.create(
                code=code,
                name=item_name,
                active=True
            )

            LaundryInventory.objects.create(
                item=code,
                quantity=qty
            )

            messages.success(request, f"Articolo '{item_name}' aggiunto.")
            return redirect("/laundry/")

        # ELIMINA ARTICOLO
        if action == "delete_item":
            item_code = request.POST.get("item_code", "").strip()

            if item_code == "":
                messages.error(request, "Articolo non valido.")
                return redirect("/laundry/")

            item_obj = LaundryItem.objects.filter(code=item_code).first()

            if not item_obj:
                messages.error(request, "Articolo non trovato.")
                return redirect("/laundry/")

            item_name = item_obj.name

            LaundryMovement.objects.filter(item=item_code).delete()
            LaundryInventory.objects.filter(item=item_code).delete()
            item_obj.delete()

            messages.success(request, f"Articolo '{item_name}' eliminato.")
            return redirect("/laundry/")

        # INVENTARIO
        if action == "set_inventory":
            items = LaundryItem.objects.filter(active=True).order_by("name")

            for item_obj in items:
                qty = request.POST.get(item_obj.code, "").strip()

                if qty != "":
                    obj, _ = LaundryInventory.objects.get_or_create(item=item_obj.code)
                    obj.quantity = int(qty)
                    if obj.quantity < 0:
                        obj.quantity = 0
                    obj.save()

            messages.success(request, "Inventario aggiornato.")
            return redirect("/laundry/")

        # MOVIMENTI
        if action == "movement":
            selected_date = request.POST.get("date")
            movement_type = request.POST.get("movement_type")
            items = LaundryItem.objects.filter(active=True).order_by("name")

            for item_obj in items:
                qty = request.POST.get(item_obj.code, "").strip()

                if qty and int(qty) > 0:
                    qty_int = int(qty)
                    inv, _ = LaundryInventory.objects.get_or_create(item=item_obj.code)

                    if movement_type in ["dirty", "remove"]:
                        if inv.quantity - qty_int < 0:
                            messages.error(
                                request,
                                f"Quantità insufficiente per {item_obj.name}. Disponibili: {inv.quantity}, richieste: {qty_int}."
                            )
                            return redirect("/laundry/")

                    LaundryMovement.objects.create(
                        date=selected_date,
                        item=item_obj.code,
                        quantity=qty_int,
                        movement_type=movement_type
                    )

                    if movement_type == "dirty":
                        inv.quantity -= qty_int
                    elif movement_type == "clean":
                        inv.quantity += qty_int
                    elif movement_type == "add":
                        inv.quantity += qty_int
                    elif movement_type == "remove":
                        inv.quantity -= qty_int

                    inv.save()

            messages.success(request, "Movimento registrato.")
            return redirect("/laundry/")

        # AZZERA STORICO FILTRATO
        if action == "clear_history":
            start_date = request.POST.get("start_date", "")
            end_date = request.POST.get("end_date", "")

            movements_to_delete = LaundryMovement.objects.all()

            if start_date:
                movements_to_delete = movements_to_delete.filter(date__gte=start_date)

            if end_date:
                movements_to_delete = movements_to_delete.filter(date__lte=end_date)

            deleted_count = movements_to_delete.count()
            movements_to_delete.delete()

            messages.success(request, f"Storico eliminato. Movimenti cancellati: {deleted_count}.")
            return redirect(f"/laundry/?start_date={start_date}&end_date={end_date}")

    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    items = LaundryItem.objects.filter(active=True).order_by("name")
    inventory = {i.item: i.quantity for i in LaundryInventory.objects.all()}
    item_names = {i.code: i.name for i in items}

    movements = LaundryMovement.objects.all().order_by("-date", "-id")

    if start_date:
        movements = movements.filter(date__gte=start_date)

    if end_date:
        movements = movements.filter(date__lte=end_date)

    context = {
        "items": items,
        "inventory": inventory,
        "item_names": item_names,
        "movements": movements[:200],
        "today": date.today(),
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "laundry/laundry.html", context)