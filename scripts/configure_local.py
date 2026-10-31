"""Create .env without printing credentials. Run locally, not through chat."""
from getpass import getpass
from pathlib import Path
import argparse
import os
import secrets
from urllib.parse import quote, urlsplit

root = Path(__file__).resolve().parent.parent
target = root / ".env"

# These values were read from this project's Supabase Connect dialog.
PROJECT_REF = "kdwncovghqyprwrhwptl"
POOLER_HOST = "aws-1-eu-central-1.pooler.supabase.com"


def pooler_urls(password):
    if not password or "\n" in password or "\r" in password:
        raise ValueError("Veritabani parolasi bos veya satir sonu iceremez.")
    base = f"postgresql://postgres.{PROJECT_REF}:{quote(password, safe='')}@{POOLER_HOST}"
    return f"{base}:6543/postgres", f"{base}:5432/postgres"

def read_url(label, expected_port):
    value = getpass(label).strip()
    try:
        parsed = urlsplit(value)
        valid = (parsed.scheme in {"postgres", "postgresql"} and parsed.hostname
                 and parsed.username and parsed.password and parsed.path == "/postgres"
                 and parsed.port == expected_port and "\n" not in value and "\r" not in value)
    except ValueError:
        valid = False
    if not valid:
        raise SystemExit(f"Gecerli Supabase pooler adresi gerekli (port {expected_port}). Deger kaydedilmedi.")
    return value


def update_password():
    if not target.exists():
        raise SystemExit(".env bulunamadi. Once normal kurulum komutunu calistirin.")
    original = target.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    keys = {"DATABASE_URL": 6543, "DATABASE_MIGRATION_URL": 5432}
    positions = {}
    connection_queries = {}
    for index, line in enumerate(lines):
        for key, port in keys.items():
            if line.startswith(key + "="):
                if key in positions:
                    raise SystemExit(f"{key} birden fazla tanimli; dosya degistirilmedi.")
                try:
                    parsed = urlsplit(line.partition("=")[2].strip())
                    valid = (
                        parsed.scheme in {"postgres", "postgresql"}
                        and parsed.hostname == POOLER_HOST
                        and parsed.username == f"postgres.{PROJECT_REF}"
                        and parsed.path == "/postgres"
                        and parsed.port == port
                    )
                except ValueError:
                    valid = False
                if not valid:
                    raise SystemExit(f"{key} beklenen projeye ait degil; dosya degistirilmedi.")
                positions[key] = index
                connection_queries[key] = parsed.query
    if positions.keys() != keys.keys():
        raise SystemExit(".env icinde iki baglanti adresi gerekli; dosya degistirilmedi.")

    print("Yalnizca veritabani baglanti parolasi degisecek; diger ayarlar korunacak.")
    try:
        password = getpass("Yeni veritabani parolasi: ")
        confirmation = getpass("Ayni parolayi tekrar girin: ")
        if password != confirmation:
            raise ValueError("Girilen iki parola ayni degil; .env degistirilmedi.")
        runtime, migration = pooler_urls(password)
    except ValueError as error:
        raise SystemExit(str(error)) from None
    for key, uri in (("DATABASE_URL", runtime), ("DATABASE_MIGRATION_URL", migration)):
        query = connection_queries[key]
        lines[positions[key]] = f"{key}={uri}{'?' + query if query else ''}\n"
    replacement = target.with_name(f".env.{secrets.token_hex(8)}.tmp")
    try:
        with replacement.open("x", encoding="utf-8") as output:
            output.writelines(lines)
        os.replace(replacement, target)
    finally:
        replacement.unlink(missing_ok=True)
    print(".env guncellendi. Parola ekrana yazdirilmadi.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gizli bilgileri yazdirmadan yerel .env olusturur.")
    parser.add_argument("--connection-urls", action="store_true", help="Farkli proje icin iki tam URI sor.")
    parser.add_argument("--update-password", action="store_true", help="Mevcut .env icindeki DB parolasini guncelle.")
    args = parser.parse_args()
    if args.update_password:
        if args.connection_urls:
            raise SystemExit("--update-password ve --connection-urls birlikte kullanilamaz.")
        update_password()
        raise SystemExit(0)
    if target.exists():
        raise SystemExit(".env zaten var. Uzerine yazilmadi; dosyayi yerel editorunuzde duzenleyin.")
    if args.connection_urls:
        print("Supabase Connect adreslerini parolalari URL-encoded olarak girin.")
        runtime = read_url("Transaction pooler URL (6543): ", 6543)
        migration = read_url("Session pooler URL (5432): ", 5432)
    else:
        print(f"Proje: kararsizim-dev ({PROJECT_REF})")
        print(f"Dogrulanmis pooler: {POOLER_HOST}")
        print("Veritabani parolanizi girin. Yazarken karakterler gorunmez.")
        print("Ozel karakterler otomatik URL-encode edilir; Supabase hesap parolanizi girmeyin.")
        try:
            runtime, migration = pooler_urls(getpass("Veritabani parolasi: "))
        except ValueError as error:
            raise SystemExit(str(error)) from None
    body = (
        f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n"
        "DJANGO_DEBUG=true\n"
        "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1\n"
        "DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000\n"
        f"DATABASE_URL={runtime}\nDATABASE_MIGRATION_URL={migration}\n"
        f"GUEST_VOTE_HASH_KEY={secrets.token_urlsafe(48)}\n"
    )
    with target.open("x", encoding="utf-8") as output:
        output.write(body)
    print(".env olusturuldu. Gizli degerler ekrana yazdirilmadi.")

