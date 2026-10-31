"""Shared PostgreSQL fixed-window limits; no raw network/account identifiers stored."""
import hashlib
import hmac
import ipaddress
from datetime import datetime, timezone as dt_timezone
from functools import wraps

from django.conf import settings
from django.db.models import F
from django.shortcuts import render
from django.utils import timezone

from .models import RateLimit


def identity_digest(value):
    return hmac.new(settings.GUEST_VOTE_HASH_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()


def client_ip(request):
    # Only Vercel settings enable its ingress-overwritten X-Forwarded-For header.
    raw = request.META.get("REMOTE_ADDR", "unknown")
    if settings.TRUST_VERCEL_PROXY:
        raw = request.META.get("HTTP_X_FORWARDED_FOR", raw).split(",")[0].strip()
    try:
        return str(ipaddress.ip_address(raw))
    except ValueError:
        return "unknown"


def consume(action, identity, limit, seconds):
    now = int(timezone.now().timestamp())
    start = now - now % seconds
    key = identity_digest(f"{action}:{identity}:{start}")
    RateLimit.objects.get_or_create(key=key, defaults={
        "expires_at": datetime.fromtimestamp(start + seconds, dt_timezone.utc),
    })
    accepted = RateLimit.objects.filter(pk=key, attempts__lt=limit).update(attempts=F("attempts") + 1)
    return bool(accepted), start + seconds - now


def rate_limit(action):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method == "POST" and settings.ABUSE_LIMITS_ENABLED:
                limit, seconds = settings.ABUSE_LIMITS[action]
                identities = ["ip:" + client_ip(request)]
                if request.user.is_authenticated:
                    identities.append("user:" + str(request.user.pk))
                elif action == "signin":
                    identities.append("login:" + request.POST.get("username", "").strip().casefold()[:254])
                for identity in identities:
                    accepted, wait = consume(action, identity, limit, seconds)
                    if not accepted:
                        response = render(request, "error.html", {"status": 429,
                            "error_message": "Çok fazla deneme yaptın. Biraz bekleyip yeniden dene."}, status=429)
                        response["Retry-After"] = str(wait)
                        return response
            return view(request, *args, **kwargs)
        return wrapped
    return decorate
