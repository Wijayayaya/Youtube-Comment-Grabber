from __future__ import annotations

from django.db.models.functions import Length
from django.utils import timezone

from ..models import LiveChatMessage, LiveStream


def enforce_display_message_length(max_length: int = 200) -> list[int]:
	"""Unselect messages exceeding the max OBS message length.

	Returns list of message IDs that were unselected.
	"""
	over_limit_ids = list(
		LiveChatMessage.objects.filter(display_selected=True)
		.annotate(message_length=Length("message_text"))
		.filter(message_length__gt=max_length)
		.values_list("id", flat=True)
	)
	if not over_limit_ids:
		return []

	LiveChatMessage.objects.filter(id__in=over_limit_ids).update(
		display_selected=False,
		is_pinned=False,
		display_order=None,
		updated_at=timezone.now(),
	)
	return over_limit_ids


def enforce_display_limit(limit: int | None = None) -> list[int]:
	"""Ensure display_selected messages do not exceed the limit.

	Pinned messages are never removed. Oldest non-pinned messages are unselected first.
	Returns list of message IDs unselected.
	"""
	stream = LiveStream.objects.order_by("-created_at").first()
	if not stream:
		return []

	limit_value = limit if limit is not None else stream.display_limit
	if not limit_value or limit_value <= 0:
		return []

	pinned_count = LiveChatMessage.objects.filter(display_selected=True, is_pinned=True).count()
	allowed_non_pinned = max(limit_value - pinned_count, 0)

	non_pinned_qs = LiveChatMessage.objects.filter(display_selected=True, is_pinned=False).order_by(
		"published_at",
		"id",
	)
	current_non_pinned = non_pinned_qs.count()
	if current_non_pinned <= allowed_non_pinned:
		return []

	remove_count = current_non_pinned - allowed_non_pinned
	to_unselect_ids = list(non_pinned_qs.values_list("id", flat=True)[:remove_count])
	if not to_unselect_ids:
		return []

	LiveChatMessage.objects.filter(id__in=to_unselect_ids).update(
		display_selected=False,
		display_order=None,
		updated_at=timezone.now(),
	)
	return to_unselect_ids
