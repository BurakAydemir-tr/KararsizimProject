from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from accounts.models import User
from polls.models import Poll, Vote


class DemoCommandTests(TestCase):
    def test_default_is_read_only_and_production_mode_refused(self):
        call_command("seed_demo", stdout=StringIO())
        self.assertFalse(User.objects.exists())
        with self.assertRaises(CommandError):
            call_command("seed_demo", apply=True, stdout=StringIO())
        # DEBUG alone must never allow writing examples into the app's postgres DB.
        with override_settings(DEBUG=True), patch("polls.management.commands.seed_demo.connection", SimpleNamespace(settings_dict={"NAME": "postgres"})):
            with self.assertRaises(CommandError):
                call_command("seed_demo", apply=True, stdout=StringIO())
        self.assertFalse(Poll.objects.exists())

    @override_settings(DEBUG=True)
    def test_explicit_seed_in_disposable_db_is_repeatable(self):
        for _ in range(2):
            call_command("seed_demo", apply=True, stdout=StringIO())
        self.assertEqual(User.objects.count(), 1)
        self.assertFalse(User.objects.get().has_usable_password())
        self.assertEqual(Poll.objects.count(), 3)
        self.assertEqual(Poll.objects.filter(closed_at__isnull=False).count(), 1)
        self.assertEqual(Vote.objects.count(), 6)
