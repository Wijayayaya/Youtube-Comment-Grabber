from __future__ import annotations

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from comments.models import LiveChatMessage, LiveStream


def store_live_chat_items(live_stream: LiveStream, items) -> int:
	saved = 0
	for item in items:
		snippet = item.get("snippet", {})
		author_details = item.get("authorDetails", {})
		published_at = parse_datetime(snippet.get("publishedAt")) or timezone.now()
		defaults = {
			"live_stream": live_stream,
			"author_name": author_details.get("displayName", ""),
			"author_channel_id": author_details.get("channelId", ""),
			"message_text": snippet.get("displayMessage", ""),
			"published_at": published_at,
			"raw_payload": item,
		}
		_, created = LiveChatMessage.objects.update_or_create(
			message_id=item.get("id"),
			defaults=defaults,
		)
		if created:
			saved += 1
	return saved
