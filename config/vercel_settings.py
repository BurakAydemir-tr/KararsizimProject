"""HTTPS-only settings for the Vercel preview; local development stays separate."""
import re
from django.core.exceptions import ImproperlyConfigured
from .settings import *  # noqa: F403
from .environment import env


DEBUG = False
DATABASE_REQUIRE_VERIFIED_TLS = True
DATABASES = {"default": database("DATABASE_URL", require_verified_tls=True)}
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
for name in ("VERCEL_URL", "VERCEL_BRANCH_URL"):
    hostname = env.str(name, default="").strip()
    if hostname:
        if not re.fullmatch(r"[a-z0-9-]+\.vercel\.app", hostname):
            raise ImproperlyConfigured(f"{name} gecerli bir Vercel hostname olmali.")
        ALLOWED_HOSTS.append(hostname)
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))
if not ALLOWED_HOSTS or any(
    not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", host)
    for host in ALLOWED_HOSTS
):
    raise ImproperlyConfigured("Vercel icin tam alan adlari gerekli; joker ALLOWED_HOSTS kullanilamaz.")

# Exact origins only: never trust every other customer's *.vercel.app deployment.
CSRF_TRUSTED_ORIGINS = ["https://" + host for host in ALLOWED_HOSTS]
for origin in env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[]):
    if origin not in CSRF_TRUSTED_ORIGINS:
        raise ImproperlyConfigured("CSRF origin HTTPS ve izinli tam alan adi ile eslesmeli.")

# Vercel terminates TLS and sets the forwarded protocol at its trusted ingress.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_REFERRER_POLICY = "same-origin"
