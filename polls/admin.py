from django.contrib import admin
from .models import Choice, Poll, Vote
from .services import manage_poll


class ChoiceInline(admin.TabularInline):
    model = Choice
    fields = ("position", "text")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("question", "author", "created_at", "closed_at", "hidden_at", "deleted_at")
    list_filter = ("hidden_at", "closed_at")
    search_fields = ("question", "author__username")
    readonly_fields = ("author", "question", "description", "created_at", "closed_at", "hidden_at", "deleted_at")
    inlines = (ChoiceInline,)
    actions = ("hide_polls", "close_polls")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Seçili anketleri herkese açık akıştan gizle")
    def hide_polls(self, request, queryset):
        for pk in queryset.order_by("pk").values_list("pk", flat=True):
            manage_poll(pk, request.user, "hide")

    @admin.action(description="Seçili anketlerin oylamasını kapat")
    def close_polls(self, request, queryset):
        for pk in queryset.order_by("pk").values_list("pk", flat=True):
            manage_poll(pk, request.user, "close")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("poll", "choice", "created_at")
    readonly_fields = ("poll", "choice", "user", "guest_identity_hash", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
