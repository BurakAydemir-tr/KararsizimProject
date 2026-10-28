"""Environment parsing shared by runtime and migration settings."""
from pathlib import Path
from urllib.parse import urlsplit

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)


def required(name):
    value = env.str(name, default="").strip()
    if not value or value.startswith("<"):
        raise ImproperlyConfigured(
            f"{name} eksik. .env.example dosyasini inceleyin veya "
            "python scripts/configure_local.py komutunu calistirin."
        )
    return value


def boolean(name, default=False):
    value = env.str(name, default=str(default)).strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    raise ImproperlyConfigured(f"{name} true veya false olmali.")


def database(name):
    raw = required(name)
    try:
        parsed = urlsplit(raw)
        port = parsed.port
        valid = (
            parsed.scheme in {"postgres", "postgresql"}
            and parsed.hostname and parsed.username and parsed.password
            and parsed.path.strip("/")
        )
        if not valid:
            raise ValueError
        config = environ.Env.db_url_config(raw)
    except (ValueError, TypeError):
        # Never echo the URL or password in error messages.
        raise ImproperlyConfigured(
            f"{name} gecerli bir PostgreSQL baglanti adresi olmali."
        ) from None
    if name == "DATABASE_MIGRATION_URL" and port == 6543:
        raise ImproperlyConfigured(
            "Migration icin transaction pooler yerine session pooler (5432) kullanin."
        )
    config["CONN_MAX_AGE"] = 0
    config["DISABLE_SERVER_SIDE_CURSORS"] = True
    config["OPTIONS"] = {
        **config.get("OPTIONS", {}),
        "sslmode": "require",
        "connect_timeout": 10,
        "prepare_threshold": None,
    }
    return config

