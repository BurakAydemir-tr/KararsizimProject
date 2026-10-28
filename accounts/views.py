from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST
from polls.services import merge_guest_votes
from .forms import SignupForm, SigninForm


def next_url(request):
    target = request.POST.get("next", request.GET.get("next", ""))
    if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return target
    return reverse("polls:home")


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("polls:home")
    form = SignupForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
                merge_guest_votes(user, request.guest_identity_hash)
        except IntegrityError:
            form.add_error(None, "Bu kullanıcı adı veya e-posta zaten kullanılıyor.")
        else:
            login(request, user)
            messages.success(request, "Aramıza hoş geldin!")
            return redirect(next_url(request))
    return render(request, "accounts/auth.html", {"form": form, "signup": True, "next": next_url(request)})


@require_http_methods(["GET", "POST"])
def signin(request):
    if request.user.is_authenticated:
        return redirect("polls:home")
    form = SigninForm(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        merge_guest_votes(user, request.guest_identity_hash)
        login(request, user)
        messages.success(request, "Giriş yaptın.")
        return redirect(next_url(request))
    return render(request, "accounts/auth.html", {"form": form, "signup": False, "next": next_url(request)})


@require_POST
def signout(request):
    logout(request)
    return redirect("polls:home")
