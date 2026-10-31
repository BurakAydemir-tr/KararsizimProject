from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone


class PollQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(deleted_at__isnull=True, hidden_at__isnull=True)


class Poll(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="polls")
    question = models.CharField("soru", max_length=200, validators=[MinLengthValidator(10)])
    description = models.CharField("açıklama", max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField("bitiş zamanı", null=True, blank=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    hidden_at = models.DateTimeField(null=True, blank=True)
    objects = PollQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["-created_at", "-id"], name="poll_feed_order"),
                   models.Index(fields=["author", "-created_at"], name="poll_author_order")]
        verbose_name = "anket"
        verbose_name_plural = "anketler"

    def __str__(self):
        return self.question

    @property
    def is_open(self):
        return not (self.closed_at or self.deleted_at or self.hidden_at or
                    (self.ends_at and self.ends_at <= timezone.now()))


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField("seçenek", max_length=100)
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["poll", "position"], name="choice_position_unique"),
            models.CheckConstraint(condition=models.Q(position__gte=1, position__lte=5), name="choice_position_range"),
            models.CheckConstraint(condition=~models.Q(text=""), name="choice_text_required"),
        ]

    def __str__(self):
        return self.text


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    choice = models.ForeignKey(Choice, on_delete=models.PROTECT, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    guest_identity_hash = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "user"], condition=models.Q(user__isnull=False), name="member_one_vote"),
            models.UniqueConstraint(fields=["poll", "guest_identity_hash"], condition=models.Q(user__isnull=True), name="guest_one_vote"),
            models.CheckConstraint(condition=models.Q(user__isnull=False) | models.Q(guest_identity_hash__regex=r"^[a-f0-9]{64}$"), name="guest_identity_required"),
        ]


class RateLimit(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    attempts = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)


class Report(models.Model):
    REASONS = [("spam", "Spam / yanıltıcı içerik"), ("abuse", "Hakaret / zararlı içerik"),
               ("privacy", "Kişisel bilgi paylaşımı"), ("other", "Diğer")]
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    identity_hash = models.CharField(max_length=64)
    reason = models.CharField(max_length=12, choices=REASONS)
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.CharField(max_length=12, choices=[("hidden", "Gizlendi"), ("dismissed", "İhlal yok")], blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    related_name="reviewed_reports", on_delete=models.SET_NULL)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["poll", "identity_hash"], name="one_report_per_identity")]


class ErrorEvent(models.Model):
    request_id = models.UUIDField(unique=True)
    route = models.CharField(max_length=120)
    error_type = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
