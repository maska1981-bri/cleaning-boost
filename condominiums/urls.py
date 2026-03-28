from django.urls import path
from .views import generate_condominium_cleanings

urlpatterns = [
    path(
        "generate-cleanings/",
        generate_condominium_cleanings,
        name="generate_condominium_cleanings",
    ),
]