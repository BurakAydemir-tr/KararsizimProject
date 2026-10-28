from pathlib import Path
from contextlib import contextmanager
from secrets import token_hex
from unittest import TestCase

from scripts.prepare_vercel_env import prepare_preview_file


@contextmanager
def preview_target():
    directory = Path(__file__).resolve().parents[1] / ".tmp"
    directory.mkdir(exist_ok=True)
    target = directory / f"preview-test-{token_hex(8)}.env"
    try:
        yield target
    finally:
        target.unlink(missing_ok=True)


class PreviewEnvTests(TestCase):
    def test_preview_file_has_separate_keys_and_never_overwrites(self):
        with preview_target() as target:
            url = "postgresql://postgres.example:encoded%3F@pooler.example:6543/postgres"
            self.assertEqual(prepare_preview_file(url, target), 7)
            original = target.read_text(encoding="utf-8")
            values = dict(line.split("=", 1) for line in original.splitlines())
            self.assertEqual(values["DATABASE_URL"], url)
            self.assertEqual(values["DJANGO_DEBUG"], "false")
            self.assertGreaterEqual(len(values["DJANGO_SECRET_KEY"]), 50)
            self.assertNotEqual(values["DJANGO_SECRET_KEY"], values["GUEST_VOTE_HASH_KEY"])
            self.assertNotIn("DATABASE_MIGRATION_URL", values)
            with self.assertRaises(FileExistsError):
                prepare_preview_file(url, target)
            self.assertEqual(target.read_text(encoding="utf-8"), original)

    def test_invalid_url_does_not_get_written_or_leaked(self):
        with preview_target() as target:
            secret_url = "postgresql://private:do-not-leak@localhost:5432/postgres"
            with self.assertRaises(ValueError) as error:
                prepare_preview_file(secret_url, target)
            self.assertNotIn("do-not-leak", str(error.exception))
            self.assertFalse(target.exists())
