from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q

from polls.models import Poll, Vote, Report


@transaction.atomic
def delete_account(user):
    if not user.is_authenticated or not user.is_active or user.is_staff:
        raise PermissionDenied
    poll_ids = list(Poll.objects.filter(author=user).order_by("pk").select_for_update().values_list("pk", flat=True))
    # Choices protect votes; remove dependent votes before their polls.
    Vote.objects.filter(Q(user=user) | Q(poll_id__in=poll_ids)).delete()
    Report.objects.filter(reporter=user).delete()
    Poll.objects.filter(pk__in=poll_ids).delete()
    user.delete()
