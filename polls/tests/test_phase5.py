import gzip
import io
import json
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.db import connection
from django.test import Client, RequestFactory, TestCase, override_settings
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from config.monitoring import ErrorMonitoringMiddleware
from polls.abuse import consume, client_ip
from polls.models import Poll, Vote, Report, ErrorEvent, RateLimit
from polls.services import create_poll, cast_vote, report_poll, resolve_report


class PhaseFiveTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user("phaseowner", "owner@example.invalid", "Valid-password!93571")
        cls.other = User.objects.create_user("phasemember", "member@example.invalid", "Valid-password!93571")
        cls.poll = create_poll(cls.owner, "Hafta sonu ne yapalım?", "", ["Park", "Sinema"])

    def test_search_excludes_hidden_and_deleted_and_preserves_pagination(self):
        for i in range(13):
            create_poll(self.owner, f"Aranabilir sorumuz {i}", "", ["A", "B"])
        hidden = create_poll(self.owner, "Aranabilir gizli sorumuz", "", ["A", "B"])
        Poll.objects.filter(pk=hidden.pk).update(hidden_at=timezone.now())
        response = self.client.get("/?q=Aranabilir")
        self.assertEqual(len(response.context["page_obj"]), 12)
        self.assertNotContains(response, hidden.question)
        self.assertContains(response, "q=Aranabilir&amp;sayfa=2")
        self.assertEqual(len(self.client.get("/?q=Aranabilir&sayfa=2").context["page_obj"]), 1)
        self.assertContains(self.client.get("/?q=<script>"), "Aramana uygun anket bulunamadı")

    def test_deadline_closes_votes_and_exposes_results_without_a_scheduler(self):
        poll = create_poll(self.owner, "Süreli bir karar verelim mi?", "", ["A", "B"], ends_at=timezone.now() + timezone.timedelta(hours=1))
        Poll.objects.filter(pk=poll.pk).update(ends_at=timezone.now() - timezone.timedelta(seconds=1))
        with self.assertRaises(ValidationError):
            cast_vote(poll.pk, poll.choices.first().pk, user=self.other)
        response = self.client.get(reverse("polls:detail", args=[poll.pk]))
        self.assertContains(response, "oylaması sona erdi")
        self.assertNotContains(response, 'data-vote-form')

    def test_creation_duration_and_duplicate_spam(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("polls:create"), {"question": "Yarın nereye gitmeliyiz?", "option_1": "A", "option_2": "B", "duration": "24"})
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(Poll.objects.get(question="Yarın nereye gitmeliyiz?").ends_at)
        with self.assertRaises(ValidationError):
            create_poll(self.owner, self.poll.question, "", ["A", "B"])

    def test_reports_are_private_and_not_automatic_censorship(self):
        self.client.get(reverse("polls:detail", args=[self.poll.pk]))
        response = self.client.post(reverse("polls:report", args=[self.poll.pk]), {"reason": "spam", "description": "Kontrol edilsin"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.count(), 1)
        self.assertContains(self.client.get(reverse("polls:detail", args=[self.poll.pk])), self.poll.question)
        self.assertNotContains(self.client.get(reverse("polls:detail", args=[self.poll.pk])), "Kontrol edilsin")
        self.client.post(reverse("polls:report", args=[self.poll.pk]), {"reason": "spam"})
        self.assertEqual(Report.objects.count(), 1)

    def test_moderation_needs_staff_and_keeps_decision(self):
        report = report_poll(self.poll.pk, user=self.other, guest_hash=None, reason="abuse", description="")
        with self.assertRaises(PermissionDenied):
            resolve_report(report.pk, self.other, hide=True)
        staff = User.objects.create_superuser("phasestaff", "staff@example.invalid", "Valid-password!93571")
        resolve_report(report.pk, staff, hide=True)
        report.refresh_from_db()
        self.assertEqual(report.reviewed_by_id, staff.pk)
        self.assertEqual(report.resolution, "hidden")
        self.assertEqual(self.client.get(reverse("polls:detail", args=[self.poll.pk])).status_code, 404)

    def test_account_delete_requires_password_confirmation_and_removes_only_owned_data(self):
        other_poll = create_poll(self.other, "Başkası hangi rengi seçsin?", "", ["A", "B"])
        cast_vote(self.poll.pk, self.poll.choices.first().pk, user=self.other)
        cast_vote(other_poll.pk, other_poll.choices.first().pk, user=self.owner)
        cast_vote(other_poll.pk, other_poll.choices.first().pk, user=self.other)
        other_client = Client()
        other_client.force_login(self.owner)
        self.client.force_login(self.owner)
        path = reverse("accounts:delete")
        self.assertEqual(self.client.get(path).status_code, 200)
        self.client.post(path, {"password": "wrong", "confirm": "on"})
        self.client.post(path, {"password": "Valid-password!93571"})
        self.assertTrue(User.objects.filter(pk=self.owner.pk).exists())
        response = self.client.post(path, {"password": "Valid-password!93571", "confirm": "on"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.owner.pk).exists())
        self.assertFalse(Poll.objects.filter(pk=self.poll.pk).exists())
        self.assertTrue(Poll.objects.filter(pk=other_poll.pk).exists())
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().user_id, self.other.pk)
        self.assertEqual(other_client.get(reverse("polls:mine")).status_code, 302)

    def test_staff_and_anonymous_cannot_delete_account_and_csrf_applies(self):
        path = reverse("accounts:delete")
        self.assertEqual(self.client.post(path).status_code, 302)
        self.client.force_login(self.owner)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        self.assertEqual(csrf_client.post(path, {"password": "Valid-password!93571", "confirm": "on"}).status_code, 403)
        self.owner.is_staff = True
        self.owner.save()
        self.assertEqual(self.client.post(path).status_code, 403)

    def test_guest_erasure_cannot_remove_member_votes(self):
        cast_vote(self.poll.pk, self.poll.choices.first().pk, user=self.other)
        self.client.get(reverse("polls:detail", args=[self.poll.pk]))
        self.client.post(reverse("polls:vote", args=[self.poll.pk]), {"choice": self.poll.choices.first().pk})
        self.assertEqual(Vote.objects.count(), 2)
        self.client.post(reverse("polls:delete_guest"), {"confirm": "yes"})
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().user_id, self.other.pk)

    @override_settings(ABUSE_LIMITS_ENABLED=True, ABUSE_LIMITS={"signin": (2, 60)})
    def test_shared_limits_return_429_without_recording_raw_identity(self):
        for _ in range(2):
            self.client.post(reverse("accounts:signin"), {"username": "nonexistent", "password": "wrong"})
        response = Client().post(reverse("accounts:signin"), {"username": "nonexistent", "password": "wrong"})
        self.assertEqual(response.status_code, 429)
        self.assertGreater(int(response["Retry-After"]), 0)
        self.assertTrue(all(len(key) == 64 for key in RateLimit.objects.values_list("key", flat=True)))
        self.assertEqual(RateLimit.objects.count(), 2)

    def test_limit_expiry_and_untrusted_forwarded_headers(self):
        request = RequestFactory().get("/", REMOTE_ADDR="192.0.2.1", HTTP_X_FORWARDED_FOR="198.51.100.2")
        self.assertEqual(client_ip(request), "192.0.2.1")
        with override_settings(TRUST_VERCEL_PROXY=True):
            self.assertEqual(client_ip(request), "198.51.100.2")
        with patch("polls.abuse.timezone.now", return_value=timezone.datetime(2026, 1, 1, tzinfo=timezone.get_default_timezone())):
            self.assertTrue(consume("test", "identity", 1, 60)[0])
            self.assertFalse(consume("test", "identity", 1, 60)[0])

    def test_error_events_exclude_exception_values(self):
        request = RequestFactory().get("/?secret=private")
        middleware = ErrorMonitoringMiddleware(lambda r: None)
        middleware.process_request(request)
        middleware.process_exception(request, ValueError("private-password"))
        event = ErrorEvent.objects.get()
        self.assertEqual(event.error_type, "ValueError")
        self.assertNotIn("private", str(event.__dict__))

    def test_operational_retention_does_not_delete_active_or_open_records(self):
        old = timezone.now() - timezone.timedelta(days=181)
        RateLimit.objects.create(key="a" * 64, expires_at=old)
        event = ErrorEvent.objects.create(request_id=uuid.uuid4(), route="test", error_type="ValueError")
        ErrorEvent.objects.filter(pk=event.pk).update(created_at=old)
        report_poll(self.poll.pk, user=self.other, guest_hash=None, reason="spam", description="")
        call_command("prune_operational_data", stdout=io.StringIO())
        self.assertFalse(RateLimit.objects.exists())
        self.assertFalse(ErrorEvent.objects.exists())
        self.assertEqual(Report.objects.count(), 1)

    def test_new_tables_are_not_exposed_to_supabase_api(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT relname, relrowsecurity FROM pg_class WHERE relname IN ('polls_report','polls_ratelimit','polls_errorevent')")
            self.assertEqual(dict(cursor.fetchall()), {"polls_report": True, "polls_ratelimit": True, "polls_errorevent": True})
            cursor.execute("SELECT count(*) FROM pg_roles r CROSS JOIN pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE r.rolname IN ('anon','authenticated','service_role') AND n.nspname='public' AND c.relname IN ('polls_report','polls_ratelimit','polls_errorevent') AND has_table_privilege(r.oid,c.oid,'SELECT,INSERT,UPDATE,DELETE')")
            self.assertEqual(cursor.fetchone()[0], 0)

    def test_privacy_and_health(self):
        self.assertContains(self.client.get(reverse("privacy")), "kişi başına kesin tek oy garantisi yoktur")
        self.assertEqual(self.client.get(reverse("health")).json(), {"status": "ok"})

    def test_backup_retention_is_dry_run_until_explicit_apply(self):
        import os
        import time
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "application-20260101T000000Z-aabbccdd.json.gz"
            old.write_bytes(b"test-only")
            os.utime(old, (time.time() - 15 * 86400,) * 2)
            current = Path(directory) / "application-20261031T000000Z-aabbccdd.json.gz"
            current.write_bytes(b"test-only")
            call_command("prune_application_backups", directory=directory, stdout=io.StringIO())
            self.assertTrue(old.exists())
            call_command("prune_application_backups", directory=directory, apply=True, stdout=io.StringIO())
            self.assertFalse(old.exists())
            self.assertTrue(current.exists())


class LimitConcurrencyTests(TransactionTestCase):
    def test_simultaneous_requests_share_one_atomic_allowance(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import close_old_connections, connections
        barrier = Barrier(2)

        def attempt():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return consume("race", "same-identity", 1, 3600)[0]
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: attempt(), range(2)))
        self.assertCountEqual(outcomes, [True, False])
