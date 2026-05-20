from django.shortcuts import redirect


class BlockDemoAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path.startswith("/admin/")
            and request.user.is_authenticated
            and request.user.username == "demo"
        ):
            return redirect("/app/")

        return self.get_response(request)