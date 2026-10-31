from django.contrib import admin
from .models import Choice, Poll, Vote, Report, ErrorEvent
from .services import manage_poll, resolve_report


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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("poll", "reason", "created_at", "resolved_at", "resolution")
    list_filter = ("resolution", "reason")
    readonly_fields = ("poll", "reporter", "reason", "description", "created_at", "resolved_at", "resolution", "reviewed_by")
    exclude = ("identity_hash",)
    actions = ("hide_reported", "dismiss_reported")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="İhlali doğrula, anketi gizle")
    def hide_reported(self, request, queryset):
        for pk in queryset.order_by("pk").values_list("pk", flat=True):
            resolve_report(pk, request.user, hide=True)

    @admin.action(description="İncele, ihlal yok olarak kapat")
    def dismiss_reported(self, request, queryset):
        for pk in queryset.order_by("pk").values_list("pk", flat=True):
            resolve_report(pk, request.user, hide=False)


@admin.register(ErrorEvent)
class ErrorEventAdmin(admin.ModelAdmin):
    list_display = ("request_id", "route", "error_type", "created_at")
    readonly_fields = list_display
    search_fields = ("request_id", "route")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
