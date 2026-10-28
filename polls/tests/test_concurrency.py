from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.core.exceptions import ValidationError
from django.db import close_old_connections, connections
from django.test import TransactionTestCase
from accounts.models import User
from polls.models import Vote
from polls.services import cast_vote, create_poll, manage_poll, merge_guest_votes


class ConcurrentVoteTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner", "owner@example.invalid", "Some-test-password!")
        self.other = User.objects.create_user("member", "member@example.invalid", "Some-test-password!")
        self.poll = create_poll(self.user, "Eşzamanlı olarak ne seçelim?", "", ["A", "B"])
        self.choice = self.poll.choices.first()

    def race(self, *operations):
        barrier = Barrier(len(operations))

        def run(operation):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                operation()
                return "ok"
            except ValidationError:
                return "rejected"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=len(operations)) as pool:
            futures = [pool.submit(run, op) for op in operations]
            return [future.result(timeout=30) for future in futures]

    def test_simultaneous_duplicate_guest_vote(self):
        operation = lambda: cast_vote(self.poll.pk, self.choice.pk, guest_hash="a" * 64)
        self.assertCountEqual(self.race(operation, operation), ["ok", "rejected"])
        self.assertEqual(Vote.objects.count(), 1)

    def test_simultaneous_duplicate_member_vote(self):
        operation = lambda: cast_vote(self.poll.pk, self.choice.pk, user=self.other)
        self.assertCountEqual(self.race(operation, operation), ["ok", "rejected"])
        self.assertEqual(Vote.objects.count(), 1)

    def test_close_and_vote_have_serial_order(self):
        self.race(lambda: cast_vote(self.poll.pk, self.choice.pk, user=self.other), lambda: manage_poll(self.poll.pk, self.user, "close"))
        self.poll.refresh_from_db()
        self.assertFalse(self.poll.is_open)
        self.assertIn(Vote.objects.count(), [0, 1])
        with self.assertRaises(ValidationError):
            cast_vote(self.poll.pk, self.choice.pk, user=self.user)

    def test_login_merge_races_with_member_vote(self):
        cast_vote(self.poll.pk, self.choice.pk, guest_hash="b" * 64)
        self.race(lambda: merge_guest_votes(self.other, "b" * 64), lambda: cast_vote(self.poll.pk, self.choice.pk, user=self.other))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().user_id, self.other.pk)

    def test_guest_vote_claimed_by_only_one_account(self):
        cast_vote(self.poll.pk, self.choice.pk, guest_hash="c" * 64)
        self.race(lambda: merge_guest_votes(self.user, "c" * 64), lambda: merge_guest_votes(self.other, "c" * 64))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertIn(Vote.objects.get().user_id, [self.user.pk, self.other.pk])
