from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.http import Http404
from django.utils import timezone

from .models import Choice, Poll, Vote, Report


def normalize_options(options):
    options = [text.strip() for text in options if text.strip()]
    if not 2 <= len(options) <= 5:
        raise ValidationError("En az 2, en fazla 5 seçenek eklemelisin.")
    if any(len(text) > 100 for text in options):
        raise ValidationError("Her seçenek en fazla 100 karakter olabilir.")
    if len({text.casefold() for text in options}) != len(options):
        raise ValidationError("Aynı seçeneği birden fazla ekleyemezsin.")
    return options


@transaction.atomic
def create_poll(author, question, description, options, *, ends_at=None):
    if not author.is_authenticated or not author.is_active:
        raise PermissionDenied
    author = get_user_model().objects.select_for_update().get(pk=author.pk)
    if not author.is_active:
        raise PermissionDenied
    options = normalize_options(options)
    if ends_at is not None and ends_at <= timezone.now():
        raise ValidationError("Bitiş zamanı gelecekte olmalı.")
    if Poll.objects.visible().filter(author=author, question__iexact=question.strip(),
                                    created_at__gte=timezone.now() - timezone.timedelta(hours=24)).exists():
        raise ValidationError("Aynı soruyu son 24 saatte zaten yayınladın.")
    poll = Poll(author=author, question=question.strip(), description=description.strip(), ends_at=ends_at)
    poll.full_clean()
    poll.save()
    Choice.objects.bulk_create([Choice(poll=poll, text=text, position=i) for i, text in enumerate(options, 1)])
    return poll


@transaction.atomic
def report_poll(poll_id, *, user, guest_hash, reason, description):
    from .abuse import identity_digest
    poll = Poll.objects.select_for_update().visible().get(pk=poll_id)
    if user.is_authenticated:
        if not user.is_active:
            raise PermissionDenied
        identity = "user:" + str(user.pk)
    elif guest_hash:
        identity = "guest:" + guest_hash
    else:
        raise ValidationError("Bildirim göndermek için çerezlere izin verip tekrar dene.")
    digest = identity_digest(identity)
    if Report.objects.filter(poll=poll, identity_hash=digest).exists():
        raise ValidationError("Bu anket için bildirimin zaten alındı.")
    report = Report(poll=poll, reporter=user if user.is_authenticated else None,
                    identity_hash=digest, reason=reason, description=description.strip())
    report.full_clean()
    report.save()
    return report


@transaction.atomic
def resolve_report(report_id, actor, *, hide):
    if not actor.is_active or not actor.is_staff:
        raise PermissionDenied
    report = Report.objects.get(pk=report_id)
    # Match poll writers' lock order, then lock the report itself.
    poll = Poll.objects.select_for_update().get(pk=report.poll_id)
    report = Report.objects.select_for_update().get(pk=report_id)
    if report.resolved_at:
        return report
    if hide:
        manage_poll(poll.pk, actor, "hide")
    report.resolution = "hidden" if hide else "dismissed"
    report.resolved_at = timezone.now()
    report.reviewed_by = actor
    report.save(update_fields=["resolution", "resolved_at", "reviewed_by"])
    return report


@transaction.atomic
def cast_vote(poll_id, choice_id, *, user=None, guest_hash=None):
    try:
        poll = Poll.objects.select_for_update().visible().get(pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404 from None
    if not poll.is_open:
        raise ValidationError("Bu anketin oylaması sona erdi.")
    if not Choice.objects.filter(pk=choice_id, poll=poll).exists():
        raise ValidationError("Bu ankete ait bir seçenek seçmelisin.")
    if user is not None:
        if not user.is_active:
            raise PermissionDenied
        identity = {"user": user}
    else:
        if not guest_hash:
            raise ValidationError("Oy verebilmek için site çerezlerine izin vermelisin. Seçimini yeniden gönder.")
        identity = {"user": None, "guest_identity_hash": guest_hash}
    if Vote.objects.filter(poll=poll, **identity).exists():
        raise ValidationError("Bu ankete zaten oy verdin.")
    try:
        with transaction.atomic():
            return Vote.objects.create(poll=poll, choice_id=choice_id, **identity)
    except IntegrityError:
        raise ValidationError("Bu ankete zaten oy verdin.") from None


@transaction.atomic
def merge_guest_votes(user, guest_hash):
    if not guest_hash:
        return
    # Every writer locks polls first; ordered locks prevent cross-poll deadlocks.
    ids = Vote.objects.filter(user__isnull=True, guest_identity_hash=guest_hash).values_list("poll_id", flat=True)
    polls = list(Poll.objects.filter(pk__in=ids).order_by("pk").select_for_update())
    for poll in polls:
        guest = Vote.objects.filter(poll=poll, user__isnull=True, guest_identity_hash=guest_hash).first()
        if guest is None:
            continue
        if Vote.objects.filter(poll=poll, user=user).exists():
            guest.delete()
        else:
            guest.user = user
            guest.save(update_fields=["user"])


@transaction.atomic
def manage_poll(poll_id, actor, action):
    try:
        poll = Poll.objects.select_for_update().get(pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404 from None
    if not actor.is_authenticated or not actor.is_active or (poll.author_id != actor.pk and not actor.is_staff):
        raise PermissionDenied
    fields = {"close": "closed_at", "remove": "deleted_at", "hide": "hidden_at"}
    if action not in fields or (action == "hide" and not actor.is_staff):
        raise PermissionDenied
    field = fields[action]
    if getattr(poll, field) is None:
        setattr(poll, field, timezone.now())
        poll.save(update_fields=[field])
    return poll
