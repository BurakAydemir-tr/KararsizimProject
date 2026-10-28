from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from accounts.forms import AdminUserCreationForm
from accounts.models import User


class UserIdentityTests(SimpleTestCase):
    def test_normalizes_identity_and_hashes_password(self):
        user = User.objects._create_user_object(
            "  BuRaK_1  ", " BURAK@Example.COM ", "test-a-long-password!42"
        )
        self.assertEqual(user.username, "burak_1")
        self.assertEqual(user.email, "burak@example.com")
        self.assertNotEqual(user.password, "test-a-long-password!42")
        self.assertTrue(user.check_password("test-a-long-password!42"))

    def test_username_boundaries_and_alphabet(self):
        for invalid in ["ab", "a" * 25, "burak!", "çağrı", "two words"]:
            with self.subTest(username=invalid), self.assertRaises(ValidationError):
                User.objects._create_user_object(invalid, "valid@example.com", "SomePassword!42")
        for valid in ["abc", "a" * 24, "burak_123"]:
            user = User(username=valid, email="valid@example.com")
            user.clean_fields(exclude=["password"])

    def test_email_required_and_valid(self):
        for invalid in ["", "   ", "not-an-email"]:
            with self.subTest(email=invalid), self.assertRaises(ValidationError):
                User.objects._create_user_object("valid_user", invalid, "SomePassword!42")

    def test_admin_creation_form_includes_required_email(self):
        form = AdminUserCreationForm()
        self.assertTrue(form.fields["email"].required)
        self.assertEqual(form.fields["username"].clean(" BuRaK "), "burak")

