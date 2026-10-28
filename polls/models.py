from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models


class PollQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(deleted_at__isnull=True, hidden_at__isnull=True)


class Poll(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="polls")
    question = models.CharField("soru", max_length=200, validators=[MinLengthValidator(10)])
    description = models.CharField("açıklama", max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
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
        return not (self.closed_at or self.deleted_at or self.hidden_at)


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
