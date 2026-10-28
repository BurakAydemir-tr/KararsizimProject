"""Development smoke test: roll back every test row; never flush the DB."""
import secrets
import uuid

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sessions.backends.db import SessionStore
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor

from accounts.forms import AdminUserCreationForm
from accounts.models import User


class Command(BaseCommand):
    help = "PostgreSQL kimlik/session kontrolleri; test satirlari geri alinir."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Bu kontrol yalnizca DEBUG=true gelistirme ortaminda calisir.")
        if connection.vendor != "postgresql":
            raise CommandError("PostgreSQL baglantisi gerekli.")
        try:
            self.verify()
        except CommandError:
            raise
        except Exception as error:
            # Database errors can contain connection information or row values.
            raise CommandError(
                f"Veritabani kontrolu tamamlanamadi ({type(error).__name__}). "
                "Baglanti ayarlarini ve migration durumunu yerel ortamda kontrol edin."
            ) from None

    def verify(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() != (1,):
                raise CommandError("PostgreSQL sorgusu beklenen sonucu vermedi.")
        executor = MigrationExecutor(connection)
        if executor.migration_plan(executor.loader.graph.leaf_nodes()):
            raise CommandError("Bekleyen migration var. Once migrate komutunu calistirin.")

        suffix = uuid.uuid4().hex[:16]
        username = f"qa_{suffix}"
        email = f"{username}@example.invalid"
        password = secrets.token_urlsafe(32)
        with transaction.atomic():
            user = User.objects.create_user(f" {username.upper()} ", f" {email.upper()} ", password)
            user.refresh_from_db()
            if user.username != username or user.email != email or not user.check_password(password):
                raise CommandError("Kimlik normalizasyonu veya parola hash kontrolu basarisiz.")
            if authenticate(username=username, password=password) != user:
                raise CommandError("Django kimlik dogrulamasi basarisiz.")
            # bulk_create bypasses model validation and exercises actual DB constraints.
            for duplicate in [
                User(username=username, email=f"second_{email}", password="!"),
                User(username=f"qb_{suffix}", email=email.upper(), password="!"),
                User(username=f"qc_{suffix}", email="", password="!"),
                User(username="INVALID!", email=f"third_{email}", password="!"),
            ]:
                try:
                    with transaction.atomic():
                        User.objects.bulk_create([duplicate])
                except IntegrityError:
                    pass
                else:
                    raise CommandError("Veritabani benzersizlik/alan kisiti eksik.")

            form = AdminUserCreationForm(data={
                "username": f"qd_{suffix}", "email": email.upper(),
                "password1": password, "password2": password,
            })
            if form.is_valid():
                raise CommandError("Admin formu yinelenen e-postayi kabul etti.")

            session = SessionStore()
            session["phase_one_check"] = True
            session.save()
            session_key = session.session_key
            if SessionStore(session_key=session_key).get("phase_one_check") is not True:
                raise CommandError("Veritabani session kaliciligi dogrulanamadi.")
            self.verify_private_tables()
            transaction.set_rollback(True)

        if User.objects.filter(username=username).exists() or SessionStore().exists(session_key):
            raise CommandError("Test verisi geri alinamadi.")
        self.stdout.write(self.style.SUCCESS(
            "OK: PostgreSQL, migration, kimlik/parola, benzersizlik, admin formu, "
            "session ve tablo erisim kontrolleri gecti. Test satirlari geri alindi."
        ))

    def verify_private_tables(self):
        tables = ["accounts_user", "django_session", "django_admin_log", "polls_poll", "polls_choice", "polls_vote"]
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.relname, c.relrowsecurity FROM pg_class c "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public' AND c.relname = ANY(%s)", [tables]
            )
            states = dict(cursor.fetchall())
            if any(not states.get(name) for name in tables):
                raise CommandError("Kullanici/session tablolarinda RLS etkin degil.")
            cursor.execute(
                "SELECT r.rolname, c.relname "
                "FROM pg_roles r CROSS JOIN pg_class c "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE r.rolname IN ('anon','authenticated','service_role') "
                "AND n.nspname = 'public' AND c.relname = ANY(%s) "
                "AND has_table_privilege(r.oid, c.oid, 'SELECT,INSERT,UPDATE,DELETE')", [tables]
            )
            if cursor.fetchall():
                raise CommandError("Dahili tablolarda beklenmeyen API rol yetkisi var.")

