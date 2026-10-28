from django.test import TestCase
from django.urls import reverse


class HomeTests(TestCase):
    def test_home_is_public_and_truthfully_empty(self):
        response = self.client.get(reverse("polls:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lang="tr"')
        self.assertContains(response, "Henüz anket yok. İlk soruyu sen sor!")
        self.assertContains(response, "ÖRNEK")
        self.assertNotContains(response, "yakında burada")
        self.assertContains(response, "/static/css/style.css")

    def test_post_is_not_an_undocumented_write_endpoint(self):
        self.assertEqual(self.client.post(reverse("polls:home")).status_code, 405)

    def test_phase_two_public_endpoints_and_creation_gate(self):
        for path in ["/uye-ol/", "/giris/"]:
            self.assertEqual(self.client.get(path).status_code, 200)
        self.assertRedirects(self.client.get("/anket/olustur/"), "/giris/?next=/anket/olustur/")

