"""Explicit offline checks ONLY: no real DB, no SQLite fallback, never deploy."""
import os

os.environ.update({
    "DJANGO_SECRET_KEY": "offline-check-only-not-a-production-key-" + "x" * 32,
    "DJANGO_DEBUG": "true",
    "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,testserver",
    "DATABASE_URL": "postgresql://offline:offline@127.0.0.1:1/offline_checks",
    "GUEST_VOTE_HASH_KEY": "offline-guest-key-" + "x" * 40,
})
from .settings import *  # noqa: F403

