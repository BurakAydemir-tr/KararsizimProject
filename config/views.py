from django.shortcuts import render


def error_page(request, status):
    return render(request, "error.html", {"status": status}, status=status)


def bad_request(request, exception=None):
    return error_page(request, 400)


def forbidden(request, exception=None):
    return error_page(request, 403)


def not_found(request, exception=None):
    return error_page(request, 404)


def server_error(request):
    return error_page(request, 500)


def csrf_failure(request, reason=""):
    if request.path.endswith("/oy/"):
        return render(request, "error.html", {"status": 403, "error_message": "Oy verebilmek için site çerezlerine izin vermelisin. Sayfayı yenileyip tekrar dene."}, status=403)
    return error_page(request, 403)
