from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from accounts.models import User
from polls.forms import PollForm
from polls.identity import COOKIE_NAME
from polls.models import Choice, Poll, Vote
from polls.services import cast_vote, create_poll, manage_poll, merge_guest_votes

PASSWORD = "A-test-password!98241"


class FlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user("author", "author@example.invalid", PASSWORD)
        cls.other = User.objects.create_user("other", "other@example.invalid", PASSWORD)
        cls.poll = create_poll(cls.author, "Bu akşam hangisini seçelim?", "Türkçe açıklama", ["Sinema", "Restoran"])
        cls.choice = cls.poll.choices.first()

    def detail_url(self, poll=None):
        return reverse("polls:detail", args=[(poll or self.poll).pk])

    def vote_url(self, poll=None):
        return reverse("polls:vote", args=[(poll or self.poll).pk])

    def login(self, client=None, user=None):
        client = client or self.client
        user = user or self.author
        return client.post(reverse("accounts:signin"), {"username": user.username.upper(), "password": PASSWORD})

    def guest_vote(self, client=None):
        client = client or self.client
        client.get(self.detail_url())
        return client.post(self.vote_url(), {"choice": self.choice.pk})

    def test_signup_create_and_guest_vote_full_flow(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": " New_User ", "email": " NEW@Example.invalid ",
            "password1": PASSWORD, "password2": PASSWORD, "next": "/anket/olustur/",
        })
        self.assertRedirects(response, "/anket/olustur/")
        user = User.objects.get(username="new_user")
        self.assertEqual(user.email, "new@example.invalid")
        self.assertTrue(user.check_password(PASSWORD))
        response = self.client.post(reverse("polls:create"), {
            "question": "  Bugün hangi etkinliği yapalım?  ", "description": "<script>test</script>",
            "option_1": " Müze ", "option_2": "Park", "option_5": "Konser 🎵",
        })
        poll = Poll.objects.get(author=user)
        self.assertRedirects(response, self.detail_url(poll))
        self.assertEqual(list(poll.choices.values_list("position", flat=True)), [1, 2, 3])
        guest = Client()
        response = guest.get(self.detail_url(poll))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, user.email)
        self.assertNotContains(response, "<script>test</script>")
        response = guest.post(self.vote_url(poll), {"choice": poll.choices.first().pk}, follow=True)
        self.assertContains(response, "Oyun kaydedildi!")
        self.assertContains(response, "%100")
        self.assertEqual(poll.votes.count(), 1)

    def test_form_enforces_limits_duplicates_and_trim(self):
        base = {"question": "Geçerli bir anket sorusu", "option_1": " A ", "option_2": "B"}
        self.assertTrue(PollForm(base).is_valid())
        invalid = [
            {"option_2": ""}, {"option_2": " a "}, {"option_6": "Altıncı"},
            {"question": "kısa"}, {"question": "x" * 201}, {"description": "x" * 501}, {"option_2": "x" * 101},
        ]
        for patch in invalid:
            with self.subTest(patch=patch):
                self.assertFalse(PollForm({**base, **patch}).is_valid())
        with self.assertRaises(ValidationError):
            create_poll(self.author, "Geçerli bir anket sorusu", "", ["1"])
        self.assertEqual(Poll.objects.count(), 1)

    def test_guest_cookie_must_return_before_first_vote(self):
        response = self.client.post(self.vote_url(), {"choice": self.choice.pk}, follow=True)
        self.assertContains(response, "çerezlerine izin vermelisin")
        self.assertEqual(Vote.objects.count(), 0)
        cookie = self.client.cookies[COOKIE_NAME]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(int(cookie["max-age"]), 180 * 86400)
        self.client.post(self.vote_url(), {"choice": self.choice.pk})
        self.assertEqual(Vote.objects.count(), 1)

    def test_tampered_cookie_is_rejected_and_replaced(self):
        self.client.cookies[COOKIE_NAME] = "forged-cookie"
        self.client.post(self.vote_url(), {"choice": self.choice.pk})
        self.assertFalse(Vote.objects.exists())
        self.assertNotEqual(self.client.cookies[COOKIE_NAME].value, "forged-cookie")

    def test_repeated_guest_and_member_votes_are_rejected(self):
        self.guest_vote()
        self.client.post(self.vote_url(), {"choice": self.poll.choices.last().pk})
        self.assertEqual(Vote.objects.count(), 1)
        self.login()
        response = self.client.post(self.vote_url(), {"choice": self.choice.pk}, follow=True)
        self.assertContains(response, "zaten oy verdin")
        other_device = Client()
        self.login(other_device)
        other_device.post(self.vote_url(), {"choice": self.choice.pk})
        self.assertEqual(Vote.objects.count(), 1)

    def test_same_browser_different_accounts_have_independent_votes(self):
        self.login()
        self.client.post(self.vote_url(), {"choice": self.choice.pk})
        cookie = self.client.cookies[COOKIE_NAME].value
        self.client.post(reverse("accounts:signout"))
        self.login(user=self.other)
        self.client.post(self.vote_url(), {"choice": self.poll.choices.last().pk})
        self.assertEqual(set(Vote.objects.values_list("user_id", flat=True)), {self.author.pk, self.other.pk})
        self.assertEqual(self.client.cookies[COOKIE_NAME].value, cookie)

    def test_guest_merge_conflict_preserves_account_vote(self):
        member_vote = cast_vote(self.poll.pk, self.choice.pk, user=self.author)
        self.guest_vote()
        self.assertEqual(Vote.objects.count(), 2)
        self.login()
        self.assertEqual(list(Vote.objects.values_list("pk", flat=True)), [member_vote.pk])

    def test_merged_vote_does_not_transfer_to_next_account(self):
        self.guest_vote()
        self.login()
        vote = Vote.objects.get()
        self.assertEqual(vote.user_id, self.author.pk)
        self.client.post(reverse("accounts:signout"))
        self.login(user=self.other)
        vote.refresh_from_db()
        self.assertEqual(vote.user_id, self.author.pk)
        self.client.post(self.vote_url(), {"choice": self.choice.pk})
        self.assertEqual(Vote.objects.count(), 2)

    def test_signup_also_merges_orphan_votes(self):
        self.guest_vote()
        self.client.post(reverse("accounts:signup"), {"username": "joiner", "email": "joiner@example.invalid", "password1": PASSWORD, "password2": PASSWORD})
        self.assertEqual(Vote.objects.get().user.username, "joiner")

    def test_invalid_choice_empty_vote_and_client_identity_ignored(self):
        another = create_poll(self.author, "Başka bir soru soralım mı?", "", ["Evet", "Hayır"])
        self.client.get(self.detail_url())
        for data in [{}, {"choice": "x"}, {"choice": another.choices.first().pk}]:
            self.client.post(self.vote_url(), data)
        self.assertFalse(Vote.objects.exists())
        self.client.post(self.vote_url(), {"choice": self.choice.pk, "user": self.author.pk, "guest_identity_hash": "spoof"})
        vote = Vote.objects.get()
        self.assertIsNone(vote.user_id)
        self.assertEqual(len(vote.guest_identity_hash), 64)

    def test_owner_confirmation_close_remove_and_permissions(self):
        self.login(user=self.other)
        for name in ["close", "remove"]:
            self.assertEqual(self.client.post(reverse(f"polls:{name}", args=[self.poll.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse("polls:confirm", args=[self.poll.pk, "close"])).status_code, 403)
        self.client.post(reverse("accounts:signout"))
        self.login()
        self.assertEqual(self.client.get(reverse("polls:close", args=[self.poll.pk])).status_code, 405)
        self.assertEqual(self.client.get(reverse("polls:remove", args=[self.poll.pk])).status_code, 405)
        self.assertEqual(self.client.get(reverse("polls:confirm", args=[self.poll.pk, "close"])).status_code, 200)
        self.poll.refresh_from_db()
        self.assertTrue(self.poll.is_open)
        self.client.post(reverse("polls:close", args=[self.poll.pk]))
        self.assertContains(self.client.get(self.detail_url()), "oylaması sona erdi")
        with self.assertRaises(ValidationError):
            cast_vote(self.poll.pk, self.choice.pk, user=self.other)
        self.client.post(reverse("polls:remove", args=[self.poll.pk]))
        self.assertEqual(self.client.get(self.detail_url()).status_code, 404)
        self.assertNotContains(self.client.get(reverse("polls:mine")), self.poll.question)

    def test_admin_moderation_and_immutable_published_content(self):
        staff = User.objects.create_superuser("adminuser", "admin@example.invalid", PASSWORD)
        poll_admin = admin.site._registry[Poll]
        vote_admin = admin.site._registry[Vote]
        request = type("Request", (), {"user": staff})()
        self.assertFalse(poll_admin.has_add_permission(request))
        self.assertFalse(poll_admin.has_delete_permission(request, self.poll))
        self.assertIn("question", poll_admin.get_readonly_fields(request, self.poll))
        self.assertFalse(vote_admin.has_add_permission(request))
        self.assertFalse(vote_admin.has_change_permission(request))
        self.assertFalse(vote_admin.has_delete_permission(request))
        self.assertNotIn(Choice, admin.site._registry)
        poll_admin.hide_polls(request, Poll.objects.filter(pk=self.poll.pk))
        self.assertEqual(self.client.get(self.detail_url()).status_code, 404)
        self.assertNotContains(self.client.get("/"), self.poll.question)
        self.assertEqual(self.client.post(self.vote_url(), {"choice": self.choice.pk}).status_code, 404)

    def test_feed_pagination_mine_and_query_count(self):
        for i in range(13):
            create_poll(self.other, f"Sıralama kontrol sorusu {i:02d}", "", ["A", "B"])
        response = self.client.get("/")
        self.assertEqual(len(response.context["page_obj"]), 12)
        self.assertEqual(len(self.client.get("/?sayfa=2").context["page_obj"]), 2)
        self.assertEqual(self.client.get("/?sayfa=bad").status_code, 200)
        self.login()
        response = self.client.get(reverse("polls:mine"))
        self.assertEqual(list(response.context["page_obj"]), [self.poll])
        self.client.post(reverse("accounts:signout"))
        # Count, card query and no per-card author/vote query.
        with self.assertNumQueries(2):
            self.client.get("/")

    def test_zero_and_tied_results_are_public_without_voter_identities(self):
        self.assertContains(self.client.get(self.detail_url()+"?sonuclar=1"), "%0", count=2)
        cast_vote(self.poll.pk, self.choice.pk, user=self.author)
        cast_vote(self.poll.pk, self.poll.choices.last().pk, user=self.other)
        body = self.client.get(self.detail_url()+"?sonuclar=1")
        self.assertContains(body, "%50", count=2)
        self.assertNotContains(body, self.other.username)
        self.assertNotContains(body, self.author.email)

    def test_safe_next_normalized_login_and_inactive_user(self):
        for target in ["https://evil.invalid/", "//evil.invalid/"]:
            self.assertRedirects(self.client.post(reverse("accounts:signin"), {"username": " AUTHOR ", "password": PASSWORD, "next": target}), "/")
            self.client.post(reverse("accounts:signout"))
        self.assertRedirects(self.client.post(reverse("accounts:signin"), {"username": "author", "password": PASSWORD, "next": "/anketlerim/"}), "/anketlerim/")
        self.assertEqual(self.client.get(reverse("accounts:signout")).status_code, 405)
        self.client.post(reverse("accounts:signout"))
        self.author.is_active = False
        self.author.save()
        self.assertContains(self.login(), "Kullanıcı adı veya parola hatalı.")

    def test_duplicate_registration_email_and_username(self):
        for username, email in [("AUTHOR", "unique@example.invalid"), ("different", "AUTHOR@EXAMPLE.INVALID")]:
            response = self.client.post(reverse("accounts:signup"), {"username": username, "email": email, "password1": PASSWORD, "password2": PASSWORD})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertEqual(User.objects.count(), 2)

    def test_empty_auth_and_creation_posts_show_validation_errors(self):
        for name in ["signup", "signin"]:
            response = self.client.post(reverse(f"accounts:{name}"), {})
            self.assertTrue(response.context["form"].errors)
        self.login()
        response = self.client.post(reverse("polls:create"), {})
        self.assertTrue(response.context["form"].errors)

    def test_csrf_enforced_on_writes(self):
        client = Client(enforce_csrf_checks=True)
        for path, data in [(self.vote_url(), {"choice": self.choice.pk}), (reverse("accounts:signup"), {}), (reverse("accounts:signin"), {}), (reverse("accounts:signout"), {})]:
            self.assertEqual(client.post(path, data).status_code, 403)
        self.assertContains(client.post(self.vote_url(), {"choice": self.choice.pk}), "site çerezlerine izin vermelisin", status_code=403)
        client.get(self.detail_url())
        response = client.post(self.vote_url(), {"choice": self.choice.pk, "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vote.objects.count(), 1)

    def test_database_constraints_are_real(self):
        cast_vote(self.poll.pk, self.choice.pk, user=self.author)
        cast_vote(self.poll.pk, self.choice.pk, guest_hash="a" * 64)
        rows = [Vote(poll=self.poll, choice=self.choice, user=self.author), Vote(poll=self.poll, choice=self.choice, guest_identity_hash="a" * 64), Vote(poll=self.poll, choice=self.choice)]
        for row in rows:
            with self.assertRaises(IntegrityError), transaction.atomic():
                Vote.objects.bulk_create([row])
        with self.assertRaises(IntegrityError), transaction.atomic():
            Choice.objects.create(poll=self.poll, text="invalid", position=6)

    @override_settings(DEBUG=False)
    def test_turkish_error_pages_and_secure_cookie(self):
        response = self.client.get("/bulunmayan-sayfa/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Bu sayfa bulunamadı.", status_code=404)
        self.assertTrue(self.client.cookies[COOKIE_NAME]["secure"])
        self.assertNotContains(response, "Traceback", status_code=404)
