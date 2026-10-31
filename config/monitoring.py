import logging
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("kararsizim.errors")


class ErrorMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.error_request_id = uuid.uuid4()

    def process_exception(self, request, exception):
        if getattr(exception, "status_code", None) in (400, 403, 404):
            return
        from django.core.exceptions import PermissionDenied, SuspiciousOperation
        from django.http import Http404
        if isinstance(exception, (PermissionDenied, SuspiciousOperation, Http404)):
            return
        route = getattr(request.resolver_match, "view_name", "unresolved") or "unresolved"
        error_type = type(exception).__name__[:80]
        # Never record exception messages, form values, query strings, cookies or user IDs.
        logger.error("request_id=%s route=%s error_type=%s", request.error_request_id, route, error_type)
        try:
            from polls.models import ErrorEvent
            ErrorEvent.objects.create(request_id=request.error_request_id, route=route[:120], error_type=error_type)
        except Exception:
            logger.error("request_id=%s error_event_store_unavailable", request.error_request_id)

    def process_response(self, request, response):
        if hasattr(request, "error_request_id"):
            response["X-Request-ID"] = str(request.error_request_id)
        return response
