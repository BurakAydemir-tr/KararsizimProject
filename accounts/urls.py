from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("uye-ol/", views.signup, name="signup"),
    path("giris/", views.signin, name="signin"),
    path("cikis/", views.signout, name="signout"),
    path("hesabimi-sil/", views.delete, name="delete"),
]
