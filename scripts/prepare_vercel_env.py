"""Prepare a git-ignored preview env file without displaying any secret."""
from pathlib import Path
import os
import secrets
from urllib.parse import urlsplit

import environ


ROOT = Path(__file__).resolve().parents[1]


def prepare_preview_file(database_url, target):
    try:
        parsed = urlsplit(database_url)
        valid = (parsed.scheme in {"postgres", "postgresql"} and parsed.hostname
                 and parsed.username and parsed.password and parsed.port == 6543
                 and parsed.path.strip("/") and "\n" not in database_url and "\r" not in database_url)
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("Gecerli transaction pooler DATABASE_URL gerekli (6543); dosya yazilmadi.")
    values = {
        "DJANGO_SETTINGS_MODULE": "config.vercel_settings",
        "DJANGO_DEBUG": "false",
        "DJANGO_ALLOWED_HOSTS": "",
        "DJANGO_CSRF_TRUSTED_ORIGINS": "",
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
        "GUEST_VOTE_HASH_KEY": secrets.token_urlsafe(48),
        "DATABASE_URL": database_url,
    }
    # Exclusive create: repeated runs must not silently rotate session/guest keys.
    with target.open("x", encoding="utf-8") as output:
        output.write("".join(f"{key}={value}\n" for key, value in values.items()))
    return len(values)


if __name__ == "__main__":
    environ.Env.read_env(ROOT / ".env", overwrite=False)
    target = ROOT / ".env.vercel.local"
    try:
        count = prepare_preview_file(os.environ.get("DATABASE_URL", ""), target)
    except FileExistsError:
        raise SystemExit(".env.vercel.local zaten var; gizli anahtarlar korunarak dosya degistirilmedi.")
    except ValueError as error:
        raise SystemExit(str(error)) from None
    print(f".env.vercel.local hazir: {count} degisken. Gizli degerler gosterilmedi.")
