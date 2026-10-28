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
            "proxy=s.SECURE_PROXY_SSL_HEADER)))"
        )
        result = subprocess.run([sys.executable, "-c", code], env=values, capture_output=True, text=True)
        return result, json.loads(result.stdout) if result.returncode == 0 else None

    def test_preview_enforces_https_and_exact_hosts_even_if_debug_requested(self):
        result, data = self.load_preview()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(data["debug"])
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
            config = database("DATABASE_URL")
        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["OPTIONS"]["sslmode"], "require")
        self.assertIsNone(config["OPTIONS"]["prepare_threshold"])
        self.assertTrue(config["DISABLE_SERVER_SIDE_CURSORS"])
        self.assertEqual(config["CONN_MAX_AGE"], 0)

    def test_migration_rejects_transaction_pooler(self):
        with patch.dict(os.environ, {"DATABASE_MIGRATION_URL": "postgresql://user:secret@localhost:6543/postgres"}):
            with self.assertRaises(ImproperlyConfigured):
                database("DATABASE_MIGRATION_URL")

