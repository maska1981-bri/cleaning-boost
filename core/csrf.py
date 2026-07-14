from django.contrib import messages
from django.middleware.csrf import rotate_token
from django.shortcuts import redirect
from django.views.csrf import csrf_failure


def custom_csrf_failure(request, reason=""):
    if request.path == "/login/":
        rotate_token(request)

        messages.warning(
            request,
            "La pagina di accesso era scaduta. Inserisci nuovamente le credenziali.",
        )

        return redirect("/login/")

    return csrf_failure(request, reason=reason)
