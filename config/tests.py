import os
from unittest.mock import patch
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase
from .environment import boolean, database, required


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

