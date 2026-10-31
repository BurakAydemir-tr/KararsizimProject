import os
from unittest.mock import patch
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase
from .environment import boolean, database, required


class VercelSettingsTests(SimpleTestCase):
    def load_preview(self, **overrides):
        import json
        import subprocess
        import sys
        values = {
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "config.vercel_settings",
            "DJANGO_SECRET_KEY": "test-preview-secret-" + "x" * 60,
            "GUEST_VOTE_HASH_KEY": "test-preview-guest-" + "x" * 40,
            "DATABASE_URL": "postgresql://offline:offline@localhost:1/preview",
            "DJANGO_ALLOWED_HOSTS": "kararsizim-preview.vercel.app",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "",
            "DJANGO_DEBUG": "true",
            "VERCEL_URL": "kararsizim-abc123.vercel.app",
            "VERCEL_BRANCH_URL": "kararsizim-git-preview.vercel.app",
            **overrides,
        }
        code = (
            "import json; from config import vercel_settings as s; "
            "print(json.dumps(dict(debug=s.DEBUG, hosts=s.ALLOWED_HOSTS, "
            "origins=s.CSRF_TRUSTED_ORIGINS, redirect=s.SECURE_SSL_REDIRECT, "
            "session_secure=s.SESSION_COOKIE_SECURE, csrf_secure=s.CSRF_COOKIE_SECURE, "
            "proxy=s.SECURE_PROXY_SSL_HEADER, tls=s.DATABASES['default']['OPTIONS']['sslmode'])))"
        )
        result = subprocess.run([sys.executable, "-c", code], env=values, capture_output=True, text=True)
        return result, json.loads(result.stdout) if result.returncode == 0 else None

    def test_preview_enforces_https_and_exact_hosts_even_if_debug_requested(self):
        result, data = self.load_preview()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(data["debug"])
        self.assertEqual(data["tls"], "verify-full")
        self.assertEqual(len(data["hosts"]), 3)
        self.assertTrue(all(origin == "https://" + host for origin, host in zip(data["origins"], data["hosts"])))
        self.assertTrue(data["redirect"] and data["session_secure"] and data["csrf_secure"])
        self.assertEqual(data["proxy"], ["HTTP_X_FORWARDED_PROTO", "https"])

    def test_preview_rejects_wildcards_unrelated_origins_and_forged_system_hosts(self):
        for patch_values in (
            {"DJANGO_ALLOWED_HOSTS": "*"},
            {"DJANGO_ALLOWED_HOSTS": ".vercel.app"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://*.vercel.app"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "http://kararsizim-preview.vercel.app"},
            {"VERCEL_URL": "evil.example"},
            {"VERCEL_URL": "https://kararsizim.vercel.app/"},
        ):
            with self.subTest(values=patch_values):
                result, _ = self.load_preview(**patch_values)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ImproperlyConfigured", result.stderr)

    def test_preview_rejects_weaker_database_tls_even_with_debug_requested(self):
        result, _ = self.load_preview(DATABASE_URL="postgresql://offline:offline@localhost:1/preview?sslmode=require")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sslmode=verify-full gerekli", result.stderr)


class EnvironmentTests(SimpleTestCase):
    def test_false_is_false_and_unknown_boolean_rejected(self):
        with patch.dict(os.environ, {"TEST_BOOL": "false"}):
            self.assertFalse(boolean("TEST_BOOL"))
        with patch.dict(os.environ, {"TEST_BOOL": "perhaps"}):
            with self.assertRaises(ImproperlyConfigured):
                boolean("TEST_BOOL")

    def test_missing_value_is_actionable(self):
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            with self.assertRaisesMessage(ImproperlyConfigured, "DATABASE_URL eksik"):
                database("DATABASE_URL")

    def test_invalid_url_does_not_leak_value(self):
        secret = "do-not-print-this-password"
        with patch.dict(os.environ, {"DATABASE_URL": f"sqlite://{secret}"}):
            with self.assertRaises(ImproperlyConfigured) as error:
                database("DATABASE_URL")
        self.assertNotIn(secret, str(error.exception))

    def test_database_enforces_pooler_safety(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:secret@localhost:6543/postgres?sslmode=disable"}):
            config = database("DATABASE_URL", require_verified_tls=False)
        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["OPTIONS"]["sslmode"], "require")
        self.assertIsNone(config["OPTIONS"]["prepare_threshold"])
        self.assertTrue(config["DISABLE_SERVER_SIDE_CURSORS"])
        self.assertEqual(config["CONN_MAX_AGE"], 0)

    def test_strict_default_and_existing_verified_options(self):
        for query in ("", "?sslmode=verify-full&sslrootcert=C%3A%2Fcerts%2Froot.crt&channel_binding=require"):
            with self.subTest(query=query), patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:secret@localhost:5432/db" + query}):
                options = database("DATABASE_URL")["OPTIONS"]
                self.assertEqual(options["sslmode"], "verify-full")
                if query:
                    self.assertEqual(options["sslrootcert"], "C:/certs/root.crt")
                    self.assertEqual(options["channel_binding"], "require")

    def test_bundled_ca_and_explicit_environment_root(self):
        from pathlib import Path
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://u:p@localhost:5432/db", "PGSSLROOTCERT": ""}):
            options = database("DATABASE_URL")["OPTIONS"]
            self.assertTrue(Path(options["sslrootcert"]).is_file())
            self.assertIn("BEGIN CERTIFICATE", Path(options["sslrootcert"]).read_text())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://u:p@localhost:5432/db", "PGSSLROOTCERT": "operator-root.crt"}):
            self.assertNotIn("sslrootcert", database("DATABASE_URL")["OPTIONS"])

    def test_strict_rejects_weaker_or_invalid_modes_without_leaking_credentials(self):
        for name in ("DATABASE_URL", "DATABASE_MIGRATION_URL", "DATABASE_TEST_ADMIN_URL"):
            for mode in ("disable", "allow", "prefer", "require", "verify-ca", "unknown", ""):
                with self.subTest(name=name, mode=mode), patch.dict(os.environ, {name: "postgresql://user:private-password@localhost:5432/db?sslmode=" + mode}):
                    with self.assertRaises(ImproperlyConfigured) as error:
                        database(name)
                    self.assertNotIn("private-password", str(error.exception))

    def test_development_preserves_stronger_modes_and_encryption_floor(self):
        for mode in (None, "disable", "allow", "prefer", "require", "verify-ca", "verify-full"):
            query = "" if mode is None else "?sslmode=" + mode
            with self.subTest(mode=mode), patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:secret@localhost:5432/db" + query}):
                options = database("DATABASE_URL", require_verified_tls=False)["OPTIONS"]
                self.assertEqual(options["sslmode"], mode if mode in {"verify-ca", "verify-full"} else "require")

    def test_duplicate_and_encoded_tls_modes_cannot_bypass_policy(self):
        for query in ("sslmode=verify-full&sslmode=require", "sslmode=require&sslmode=verify-full", "ssl%6dode=require"):
            with self.subTest(query=query), patch.dict(os.environ, {"DATABASE_URL": "postgresql://u:p@localhost:5432/db?" + query}):
                with self.assertRaises(ImproperlyConfigured):
                    database("DATABASE_URL")

    def test_settings_consumers_use_explicit_tls_policy(self):
        import subprocess
        import sys
        for module, debug, expected in (("settings", "false", "verify-full"), ("settings", "true", "require"), ("migration_settings", "false", "verify-full"), ("migration_settings", "true", "require"), ("test_settings", "false", "verify-full"), ("test_settings", "true", "require")):
            with self.subTest(module=module, debug=debug):
                values = {**os.environ, "DJANGO_DEBUG": debug,
                          "DATABASE_URL": "postgresql://u:p@localhost:5432/db",
                          "DATABASE_MIGRATION_URL": "postgresql://postgres.project:p@aws-1-region.pooler.supabase.com:5432/db",
                          "DATABASE_TEST_ADMIN_URL": ""}
                code = "import sys; sys.argv=['manage.py','test']; from config import " + module + " as s; db=s.DATABASES['default']; assert db['OPTIONS']['sslmode']==" + repr(expected)
                if module == "test_settings":
                    code += "; assert db['HOST']=='db.project.supabase.co'; assert db['TEST']['NAME'].startswith('test_kararsizim_')"
                result = subprocess.run([sys.executable, "-c", code], env=values, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_test_admin_url_keeps_endpoint_and_certificate_options(self):
        import subprocess
        import sys
        values = {**os.environ, "DJANGO_DEBUG": "false",
                  "DATABASE_URL": "postgresql://u:p@localhost:5432/db",
                  "DATABASE_MIGRATION_URL": "postgresql://u:p@localhost:5432/db",
                  "DATABASE_TEST_ADMIN_URL": "postgresql://u:p@admin.example:5432/db?sslmode=verify-full&sslrootcert=C%3A%2Fcerts%2Fadmin.crt"}
        code = ("import sys; sys.argv=['manage.py','test']; from config import test_settings as s; "
                "db=s.DATABASES['default']; assert db['HOST']=='admin.example'; "
                "assert db['OPTIONS']['sslmode']=='verify-full'; "
                "assert db['OPTIONS']['sslrootcert']=='C:/certs/admin.crt'")
        result = subprocess.run([sys.executable, "-c", code], env=values, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_migration_rejects_transaction_pooler(self):
        with patch.dict(os.environ, {"DATABASE_MIGRATION_URL": "postgresql://user:secret@localhost:6543/postgres"}):
            with self.assertRaises(ImproperlyConfigured):
                database("DATABASE_MIGRATION_URL")

