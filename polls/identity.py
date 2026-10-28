import hashlib
import hmac
import re
import secrets

from django.conf import settings
from django.core.signing import BadSignature
from django.utils.cache import patch_cache_control

COOKIE_NAME = "kararsizim_guest"
COOKIE_SALT = "kararsizim.guest.v1"
COOKIE_AGE = 60 * 60 * 24 * 180


class GuestIdentityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            identity = request.get_signed_cookie(COOKIE_NAME, salt=COOKIE_SALT, max_age=COOKIE_AGE)
            if not re.fullmatch(r"[A-Za-z0-9_-]{43}", identity):
                identity = None
        except (KeyError, BadSignature):
            identity = None
        request.guest_identity_hash = (
            hmac.new(settings.GUEST_VOTE_HASH_KEY.encode(), identity.encode(), hashlib.sha256).hexdigest()
            if identity else None
        )
        response = self.get_response(request)
        if not identity:
            response.set_signed_cookie(
                COOKIE_NAME, secrets.token_urlsafe(32), salt=COOKIE_SALT, max_age=COOKIE_AGE,
                httponly=True, secure=not settings.DEBUG, samesite="Lax",
            )
        patch_cache_control(response, private=True, no_store=True)
        return response
