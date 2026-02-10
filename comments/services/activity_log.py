from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from ..models import ActivityLog, LiveChatMessage, LiveStream


def _get_ip_address(request: HttpRequest | None) -> str | None:
	if not request:
		return None
	forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if forwarded_for:
		return forwarded_for.split(',')[0].strip()
	return request.META.get('REMOTE_ADDR')


def log_activity(
	request: HttpRequest | None,
	action: str,
	message: LiveChatMessage | None = None,
	livestream: LiveStream | None = None,
	details: dict[str, Any] | None = None,
) -> ActivityLog:
	user = getattr(request, 'user', None)
	if user is not None and not user.is_authenticated:
		user = None

	return ActivityLog.objects.create(
		user=user,
		action=action,
		message=message,
		livestream=livestream,
		details=details or {},
		ip_address=_get_ip_address(request),
	)
