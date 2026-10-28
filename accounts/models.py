from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models.functions import Lower

username_validator = RegexValidator(
    regex=r"\A[a-z0-9_]{3,24}\Z",
    message="Kullanıcı adı 3–24 karakter olmalı; a-z, 0-9 ve alt çizgi kullanılabilir.",
)


class UserManager(DjangoUserManager):
    @classmethod
    def normalize_email(cls, email):
        return (email or "").strip().lower()

    def _create_user_object(self, username, email, password, **extra_fields):
        user = super()._create_user_object(username, email, password, **extra_fields)
        user.normalize_identity()
        user.full_clean(validate_unique=False, validate_constraints=False)
        return user


class User(AbstractUser):
    username = models.CharField(
        "kullanıcı adı", max_length=24, unique=True,
        validators=[username_validator, MinLengthValidator(3)],
        help_text="3–24 karakter: a-z, 0-9 ve alt çizgi. Türkçe harf kullanmayın.",
        error_messages={"unique": "Bu kullanıcı adı zaten kullanılıyor."},
    )
    email = models.EmailField("e-posta adresi", blank=False)
    objects = UserManager()

    class Meta:
        verbose_name = "kullanıcı"
        verbose_name_plural = "kullanıcılar"
        constraints = [
            models.UniqueConstraint(Lower("username"), name="user_username_ci_unique"),
            models.UniqueConstraint(Lower("email"), name="user_email_ci_unique"),
            models.CheckConstraint(
                condition=models.Q(username__regex=r"^[a-z0-9_]{3,24}$"),
                name="user_username_format",
            ),
            models.CheckConstraint(
                condition=~models.Q(email=""), name="user_email_not_empty"
            ),
        ]

    @classmethod
    def normalize_username(cls, username):
        return super().normalize_username(username or "").strip().lower()

    def normalize_identity(self):
        self.username = self.normalize_username(self.username)
        self.email = type(self).objects.normalize_email(self.email)

    def clean(self):
        super().clean()
        self.normalize_identity()

    def clean_fields(self, exclude=None):
        self.normalize_identity()
        return super().clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        self.normalize_identity()
        # Validate fields even for ordinary model.save(); DB constraints handle races.
        self.clean_fields()
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"username", "email"}
        return super().save(*args, **kwargs)

