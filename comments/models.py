from django.db import models
from django.utils import timezone


class LiveStream(models.Model):
	"""Represents a YouTube live stream we want to monitor."""
	video_id = models.CharField(max_length=64, unique=True)
	title = models.CharField(max_length=255, blank=True)
	is_active = models.BooleanField(default=True)
	last_live_chat_id = models.CharField(max_length=255, blank=True)
	next_page_token = models.CharField(max_length=255, blank=True)
	last_polled_at = models.DateTimeField(null=True, blank=True)
	# OBS integration: reference to shared OBS config
	obs_config = models.ForeignKey(
		'OBSConfig', null=True, blank=True, on_delete=models.SET_NULL, related_name='streams'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return f"{self.title or self.video_id}"



class OBSConfig(models.Model):
	"""Shared OBS websocket configuration used by one or more LiveStream entries."""

	name = models.CharField(max_length=128, unique=True, help_text='Friendly name for this OBS connection')
	host = models.CharField(max_length=255, help_text='OBS websocket host, e.g. 127.0.0.1')
	port = models.PositiveIntegerField(default=4444, help_text='OBS websocket port')
	password = models.CharField(max_length=255, blank=True, help_text='OBS websocket password (optional)')
	default_text_source = models.CharField(max_length=255, blank=True, help_text='Default text source name in OBS')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']

	def __str__(self) -> str:
		return self.name


class LiveChatMessage(models.Model):
	class Status(models.TextChoices):
		NEW = 'new', 'Baru'
		REVIEWED = 'reviewed', 'Ditinjau'
		SENT = 'sent', 'Terkirim'
		IGNORED = 'ignored', 'Diabaikan'

	live_stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name='messages')
	message_id = models.CharField(max_length=255, unique=True)
	author_name = models.CharField(max_length=255)
	author_channel_id = models.CharField(max_length=255, blank=True)
	author_profile_image_url = models.URLField(max_length=500, blank=True)
	# Mark message to be shown in OBS browser source
	obs_selected = models.BooleanField(default=False)
	message_text = models.TextField()
	published_at = models.DateTimeField()
	status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
	note = models.TextField(blank=True)
	sent_at = models.DateTimeField(null=True, blank=True)
	raw_payload = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-published_at']

	def __str__(self) -> str:
		return f"{self.author_name}: {self.message_text[:40]}"

	def mark_sent(self, note: str | None = None):
		if note is not None:
			self.note = note
		self.status = self.Status.SENT
		self.sent_at = timezone.now()
		self.save(update_fields=['status', 'note', 'sent_at', 'updated_at'])
