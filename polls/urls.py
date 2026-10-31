from django.urls import path
from . import views

app_name = "polls"
urlpatterns = [
    path("", views.home, name="home"),
    path("misafir-oylarimi-sil/", views.delete_guest, name="delete_guest"),
    path("anket/olustur/", views.create, name="create"),
    path("anketlerim/", views.mine, name="mine"),
    path("anket/<int:pk>/", views.detail, name="detail"),
    path("anket/<int:pk>/oy/", views.vote, name="vote"),
    path("anket/<int:pk>/bildir/", views.report, name="report"),
    path("anket/<int:pk>/onay/<str:action>/", views.confirm, name="confirm"),
    path("anket/<int:pk>/kapat/", views.close, name="close"),
    path("anket/<int:pk>/kaldir/", views.remove, name="remove"),
]

