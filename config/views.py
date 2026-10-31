from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_safe


def error_page(request, status):
    return render(request, "error.html", {"status": status}, status=status)


def bad_request(request, exception=None):
    return error_page(request, 400)


def forbidden(request, exception=None):
    return error_page(request, 403)


def not_found(request, exception=None):
    return error_page(request, 404)


def server_error(request):
    return render(request, "error.html", {"status": 500,
        "request_id": getattr(request, "error_request_id", None)}, status=500)


@require_safe
def privacy(request):
    return render(request, "privacy.html")


@require_safe
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            healthy = cursor.fetchone() == (1,)
    except Exception:
        healthy = False
    response = JsonResponse({"status": "ok" if healthy else "unavailable"}, status=200 if healthy else 503)
    response["Cache-Control"] = "private, no-store"
    return response


def csrf_failure(request, reason=""):
    if request.path.endswith("/oy/"):
        return render(request, "error.html", {"status": 403, "error_message": "Oy verebilmek için site çerezlerine izin vermelisin. Sayfayı yenileyip tekrar dene."}, status=403)
    return error_page(request, 403)
