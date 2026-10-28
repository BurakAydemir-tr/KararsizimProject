from unittest import TestCase
from unittest.mock import patch
from pathlib import Path
from secrets import token_hex
from urllib.parse import unquote, urlsplit
from . import configure_local
from .configure_local import pooler_urls

TEST_TMP = Path(__file__).resolve().parent.parent / ".tmp"
TEST_TMP.mkdir(exist_ok=True)


def test_target():
    return TEST_TMP / f"test_{token_hex(8)}.env"


class ConfigureLocalTests(TestCase):
    def test_password_special_characters_are_encoded(self):
        password = "p@ss:/?#% $'value"
        runtime, migration = pooler_urls(password)
        for uri, port in [(runtime, 6543), (migration, 5432)]:
            parts = urlsplit(uri)
            self.assertEqual(unquote(parts.password), password)
            self.assertEqual(parts.port, port)
            self.assertEqual(parts.path, "/postgres")
            self.assertFalse(parts.query or parts.fragment)
        self.assertNotIn(password, runtime)

    def test_empty_or_multiline_password_rejected(self):
        for value in ["", "a\nb", "a\rb"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                pooler_urls(value)

    def test_password_update_preserves_other_settings(self):
        old_runtime, old_migration = pooler_urls("old_password")
        target = test_target()
        try:
            target.write_text(
                f"DJANGO_SECRET_KEY=keep-me\nDATABASE_URL={old_runtime}\n"
                f"DATABASE_MIGRATION_URL={old_migration}\nGUEST_VOTE_HASH_KEY=keep-this\n",
                encoding="utf-8",
            )
            with patch.object(configure_local, "target", target), patch.object(
                configure_local, "getpass", side_effect=["new@password", "new@password"]
            ):
                configure_local.update_password()
            body = target.read_text(encoding="utf-8")
            self.assertIn("DJANGO_SECRET_KEY=keep-me\n", body)
            self.assertIn("GUEST_VOTE_HASH_KEY=keep-this\n", body)
            self.assertNotIn("old_password", body)
            self.assertNotIn("new@password", body)
            self.assertEqual(body.count("DATABASE_URL="), 1)
            self.assertEqual(body.count("DATABASE_MIGRATION_URL="), 1)
        finally:
            target.unlink(missing_ok=True)

    def test_password_update_rejects_mismatched_entry(self):
        old_runtime, old_migration = pooler_urls("old_password")
        original = f"DATABASE_URL={old_runtime}\nDATABASE_MIGRATION_URL={old_migration}\n"
        target = test_target()
        try:
            target.write_text(original, encoding="utf-8")
            with patch.object(configure_local, "target", target), patch.object(
                configure_local, "getpass", side_effect=["one", "two"]
            ), self.assertRaises(SystemExit):
                configure_local.update_password()
            self.assertEqual(target.read_text(encoding="utf-8"), original)
        finally:
            target.unlink(missing_ok=True)

    def test_password_update_rejects_other_project(self):
        target = test_target()
        try:
            original = (
                "DATABASE_URL=postgresql://x:y@other-host:6543/postgres\n"
                "DATABASE_MIGRATION_URL=postgresql://x:y@other-host:5432/postgres\n"
            )
            target.write_text(original, encoding="utf-8")
            with patch.object(configure_local, "target", target), self.assertRaises(SystemExit):
                configure_local.update_password()
            self.assertEqual(target.read_text(encoding="utf-8"), original)
        finally:
            target.unlink(missing_ok=True)

