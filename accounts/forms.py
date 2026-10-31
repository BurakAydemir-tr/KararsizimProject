from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm, UsernameField
from django.core.exceptions import ValidationError
from .models import User
from django import forms


class NormalizedUsernameField(UsernameField):
    def to_python(self, value):
        return User.normalize_username(super().to_python(value))


class AdminUserCreationForm(UserCreationForm):
    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Bu e-posta zaten kullanılıyor.")
        return email

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        field_classes = {"username": NormalizedUsernameField}


class AdminUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
        field_classes = {"username": NormalizedUsernameField}


class SignupForm(AdminUserCreationForm):
    pass


class DeleteAccountForm(forms.Form):
    password = forms.CharField(label="Mevcut parolan", widget=forms.PasswordInput)
    confirm = forms.BooleanField(label="Hesabımın, anketlerimin ve oylarımın kalıcı olarak silinmesini onaylıyorum.")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise ValidationError("Parola doğrulanamadı.")
        return password


class SigninForm(AuthenticationForm):
    username = NormalizedUsernameField(label="Kullanıcı adı")
    error_messages = {
        "invalid_login": "Kullanıcı adı veya parola hatalı.",
        "inactive": "Kullanıcı adı veya parola hatalı.",
    }

