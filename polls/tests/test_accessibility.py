from html.parser import HTMLParser

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from polls.services import cast_vote, create_poll, manage_poll


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class AccessibleFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("uzun_kullanici_adi_12345", "private@example.invalid", "Test-password!34892")

    def assert_references_exist(self, response):
        elements = Elements(response.content.decode()).elements
        ids = [attrs["id"] for _, attrs in elements if "id" in attrs]
        self.assertEqual(len(ids), len(set(ids)))
        for _, attrs in elements:
            references = attrs.get("aria-describedby", "").split()
            if "for" in attrs:
                references.append(attrs["for"])
            for reference in references:
                self.assertIn(reference, ids)

    def test_error_fields_have_help_error_references_and_summary_targets(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("polls:create"), {
            "question": "kısa", "option_1": "Bir seçenek", "option_2": "İkinci seçenek",
            "option_5": "ç" * 101,
        })
        self.assertContains(response, 'data-error-summary')
        self.assertContains(response, 'href="#id_question"')
        self.assertContains(response, 'href="#id_option_5"')
        self.assertContains(response, 'aria-invalid="true"', count=2)
        self.assertContains(response, "Bir seçenek")
        self.assert_references_exist(response)
        for name in ("signup", "signin"):
            response = self.client.post(reverse(f"accounts:{name}"), {})
            self.assert_references_exist(response)

    def test_maximum_turkish_content_remains_escaped_and_public_without_email(self):
        question = ("Çığışöğüİ" * 25)[:200]
        options = [(str(i) + "ğ" * 99) for i in range(5)]
        poll = create_poll(self.user, question, "<script>alert(1)</script>" + "ü" * 470, options)
        url = reverse("polls:detail", args=[poll.pk])
        response = self.client.get(url)
        self.assertContains(response, question)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert")
        self.assertNotContains(response, self.user.email)
        self.assertContains(response, 'name="choice"', count=5)
        self.assert_references_exist(response)
        # A normal form POST works independently of the enhancement script.
        response = self.client.post(reverse("polls:vote", args=[poll.pk]), {"choice": poll.choices.first().pk}, follow=True)
        self.assertContains(response, "Oyun kaydedildi!")
        self.assertContains(response, "%100")

    def test_closed_poll_explains_state_even_to_someone_who_already_voted(self):
        poll = create_poll(self.user, "Bugün hangi yolu seçelim?", "", ["Kısa yol", "Manzaralı yol"])
        cast_vote(poll.pk, poll.choices.first().pk, user=self.user)
        manage_poll(poll.pk, self.user, "close")
        self.client.force_login(self.user)
        response = self.client.get(reverse("polls:detail", args=[poll.pk]))
        self.assertContains(response, "oylaması sona erdi")
        self.assertContains(response, "Bu ankete oy verdin")
        self.assertNotContains(response, "data-vote-form")
        self.assert_references_exist(response)

    @override_settings(
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
        SECURE_SSL_REDIRECT=True,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
    )
    def test_https_proxy_accepts_own_origin_and_rejects_another_vercel_origin(self):
        url = reverse("accounts:signin")
        client = Client(enforce_csrf_checks=True, HTTP_HOST="testserver", HTTP_X_FORWARDED_PROTO="https")
        response = client.get(url)
        self.assertEqual(response.status_code, 200)  # no redirect loop behind TLS proxy
        self.assertTrue(response.wsgi_request.is_secure())
        self.assertEqual(response.wsgi_request.get_host(), "testserver")
        self.assertTrue(client.cookies["csrftoken"]["secure"])
        credentials = {
            "username": self.user.username,
            "password": "Test-password!34892",
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        }
        self.assertEqual(client.post(url, credentials, HTTP_ORIGIN="https://unrelated.vercel.app").status_code, 403)
        response = client.post(url, credentials, HTTP_ORIGIN="https://testserver")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(client.cookies["sessionid"]["secure"])

