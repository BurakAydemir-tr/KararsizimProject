"""Real PostgreSQL tests in a newly created, disposable database only."""
import uuid
import sys
from django.core.exceptions import ImproperlyConfigured

if len(sys.argv) < 2 or sys.argv[1] != "test":
    raise ImproperlyConfigured("config.test_settings yalnizca manage.py test komutuyla kullanilabilir.")

from .settings import *  # noqa: F403
from .environment import database, env

DEBUG = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES = {"default": database("DATABASE_MIGRATION_URL")}
db = DATABASES["default"]
if env.str("DATABASE_TEST_ADMIN_URL", default=""):
    db = DATABASES["default"] = database("DATABASE_TEST_ADMIN_URL")
elif db["HOST"].endswith(".pooler.supabase.com") and db["USER"].startswith("postgres."):
    project_ref = db["USER"].split(".", 1)[1]
    db.update(HOST=f"db.{project_ref}.supabase.co", USER="postgres", PORT=5432)
db["TEST"] = {"NAME": "test_kararsizim_" + uuid.uuid4().hex[:12]}
db["OPTIONS"]["options"] = "-c lock_timeout=10000 -c statement_timeout=30000"
# A fresh name prevents accidentally dropping an existing database with --noinput.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
