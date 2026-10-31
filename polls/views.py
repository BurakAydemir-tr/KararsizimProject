from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from .forms import PollForm, VoteForm, ReportForm
from .abuse import rate_limit
from .models import Poll, Vote
from .services import cast_vote, create_poll, manage_poll, report_poll


def cards(queryset, page):
    return Paginator(queryset.select_related("author").annotate(total_votes=Count("votes")).order_by("-created_at", "-id"), 12).get_page(page)

@require_safe
def home(request):
    query = request.GET.get("q", "").strip()[:100]
    polls = Poll.objects.visible()
    if query:
        polls = polls.filter(Q(question__icontains=query) | Q(description__icontains=query))
    return render(request, "polls/home.html", {"page_obj": cards(polls, request.GET.get("sayfa")), "query": query})


@require_safe
def detail(request, pk):
    poll = get_object_or_404(Poll.objects.visible().select_related("author"), pk=pk)
    choices = list(poll.choices.annotate(vote_count=Count("votes")))
    total = sum(choice.vote_count for choice in choices)
    for choice in choices:
        choice.percent = round(choice.vote_count * 100 / total) if total else 0
    own_vote = None
    if request.user.is_authenticated:
        own_vote = Vote.objects.filter(poll=poll, user=request.user).select_related("choice").first()
    elif request.guest_identity_hash:
        own_vote = Vote.objects.filter(poll=poll, user__isnull=True, guest_identity_hash=request.guest_identity_hash).select_related("choice").first()
    return render(request, "polls/detail.html", {
        "poll": poll, "choices": choices, "total": total, "own_vote": own_vote,
        "show_results": bool(own_vote or not poll.is_open or request.GET.get("sonuclar")),
        "can_manage": request.user.is_authenticated and (request.user.pk == poll.author_id or request.user.is_staff),
    })


@login_required
@require_http_methods(["GET", "POST"])
@rate_limit("create")
def create(request):
    form = PollForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        duration = form.cleaned_data["duration"]
        try:
            poll = create_poll(request.user, form.cleaned_data["question"], form.cleaned_data["description"], form.cleaned_data["options"],
                               ends_at=timezone.now() + timezone.timedelta(hours=int(duration)) if duration else None)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Anketin yayınlandı!")
            return redirect("polls:detail", pk=poll.pk)
    return render(request, "polls/create.html", {"form": form})


@require_POST
@rate_limit("vote")
def vote(request, pk):
    get_object_or_404(Poll.objects.visible(), pk=pk)
    form = VoteForm(request.POST)
    if form.is_valid():
        try:
            cast_vote(pk, form.cleaned_data["choice"], user=request.user if request.user.is_authenticated else None, guest_hash=request.guest_identity_hash)
        except ValidationError as error:
            messages.error(request, " ".join(error.messages))
        else:
            messages.success(request, "Oyun kaydedildi!")
            return redirect(reverse("polls:detail", kwargs={"pk": pk}) + "?sonuclar=1")
    else:
        messages.error(request, " ".join(error for errors in form.errors.values() for error in errors))
    return redirect("polls:detail", pk=pk)


@login_required
@require_safe
def mine(request):
    polls = Poll.objects.filter(author=request.user, deleted_at__isnull=True)
    return render(request, "polls/mine.html", {"page_obj": cards(polls, request.GET.get("sayfa"))})


@login_required
@require_safe
def confirm(request, pk, action):
    poll = get_object_or_404(Poll, pk=pk, deleted_at__isnull=True)
    if poll.author_id != request.user.pk and not request.user.is_staff:
        raise PermissionDenied
    if action not in {"close", "remove"}:
        raise PermissionDenied
    return render(request, "polls/confirm.html", {"poll": poll, "action": action})


@login_required
@require_POST
def close(request, pk):
    manage_poll(pk, request.user, "close")
    messages.success(request, "Anketin oylaması kapatıldı.")
    return redirect("polls:mine")


@login_required
@require_POST
def remove(request, pk):
    manage_poll(pk, request.user, "remove")
    messages.success(request, "Anket kaldırıldı.")
    return redirect("polls:mine")


@require_http_methods(["GET", "POST"])
@rate_limit("report")
def report(request, pk):
    poll = get_object_or_404(Poll.objects.visible(), pk=pk)
    form = ReportForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            report_poll(pk, user=request.user, guest_hash=request.guest_identity_hash, **form.cleaned_data)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Bildirimin alındı. Yönetici inceleyecek.")
            return redirect("polls:detail", pk=pk)
    return render(request, "polls/report.html", {"poll": poll, "form": form})


@require_http_methods(["GET", "POST"])
@rate_limit("delete_account")
def delete_guest(request):
    if request.method == "POST" and request.POST.get("confirm") == "yes":
        if request.guest_identity_hash:
            Vote.objects.filter(user__isnull=True, guest_identity_hash=request.guest_identity_hash).delete()
        messages.success(request, "Bu tarayıcı kimliğine bağlı sahipsiz misafir oyları silindi.")
        response = redirect("privacy")
        response.delete_cookie("kararsizim_guest", samesite="Lax")
        return response
    return render(request, "polls/delete_guest.html")

