from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AdminUserChangeForm, AdminUserCreationForm
from .models import User


@admin.register(User)
class KararsizimUserAdmin(UserAdmin):
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    list_display = ("username", "email", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email")
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("username", "email", "password1", "password2")}),
    )

