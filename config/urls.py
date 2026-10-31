from django.contrib import admin
from django.urls import include, path
from . import views

admin.site.site_header = "Kararsızım Yönetimi"
admin.site.site_title = "Kararsızım"
admin.site.index_title = "Yönetim"
urlpatterns = [
    path("", include("accounts.urls")),
    path("", include("polls.urls")),
    path("admin/", admin.site.urls),
    path("gizlilik/", views.privacy, name="privacy"),
    path("health/", views.health, name="health"),
]
handler400 = "config.views.bad_request"
handler403 = "config.views.forbidden"
handler404 = "config.views.not_found"
handler500 = "config.views.server_error"

