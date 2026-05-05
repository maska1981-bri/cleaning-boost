from django.shortcuts import render, redirect


def landing_page(request):
    if request.user.is_authenticated:
        return redirect("/app/")
    return render(request, "landing.html")