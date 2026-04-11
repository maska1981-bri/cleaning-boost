from django import forms
from django.contrib import admin
from .models import Booking
from apartments.models import Apartment


class BookingAdminForm(forms.ModelForm):
    apartment_max_guests = forms.CharField(
        label="Max ospiti immobile",
        required=False,
        disabled=True
    )

    apartment_beds = forms.CharField(
        label="Letti totali immobile",
        required=False,
        disabled=True
    )

    apartment_google_maps = forms.CharField(
        label="Google Maps",
        required=False,
        disabled=True
    )

    apartment_notes = forms.CharField(
        label="Note operative immobile",
        required=False,
        disabled=True,
        widget=forms.Textarea(attrs={"rows": 5})
    )

    class Meta:
        model = Booking
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        apartment = None

        if self.instance and self.instance.pk and self.instance.apartment:
            apartment = self.instance.apartment

        if apartment is None and request is not None:
            apartment_id = request.POST.get("apartment") or request.GET.get("apartment")
            if apartment_id:
                try:
                    apartment = Apartment.objects.get(pk=apartment_id)
                except (Apartment.DoesNotExist, ValueError, TypeError):
                    apartment = None

        if apartment:
            self.fields["apartment_max_guests"].initial = apartment.max_guests
            self.fields["apartment_beds"].initial = f"{apartment.double_beds}M / {apartment.single_beds}S"
            self.fields["apartment_google_maps"].initial = apartment.google_maps_url or "-"
            self.fields["apartment_notes"].initial = apartment.operational_notes or "-"
        else:
            self.fields["apartment_max_guests"].initial = "-"
            self.fields["apartment_beds"].initial = "-"
            self.fields["apartment_google_maps"].initial = "-"
            self.fields["apartment_notes"].initial = "-"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm

    list_display = (
        "apartment",
        "guest_name",
        "people_count",
        "double_beds",
        "single_beds",
        "check_in",
        "check_in_time",
        "check_out",
        "check_out_time",
    )

    list_filter = (
        "check_in",
        "check_out",
        "apartment",
    )

    search_fields = (
        "guest_name",
        "apartment__name",
        "apartment__code",
        "notes",
    )

    fields = (
        "apartment",
        "apartment_max_guests",
        "apartment_beds",
        "apartment_google_maps",
        "apartment_notes",
        "guest_name",
        "people_count",
        ("double_beds", "single_beds"),
        ("check_in", "check_in_time"),
        ("check_out", "check_out_time"),
        "notes",
    )

    def get_form(self, request, obj=None, **kwargs):
        base_form = super().get_form(request, obj, **kwargs)

        class RequestAwareForm(base_form):
            def __init__(self2, *args, **kw):
                kw["request"] = request
                super().__init__(*args, **kw)

        return RequestAwareForm