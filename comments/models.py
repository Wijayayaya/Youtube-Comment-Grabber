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
	# Display rotation: seconds each selected comment is shown
	display_rotation_seconds = models.PositiveIntegerField(default=6, help_text='Seconds each comment is shown in the display')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return f"{self.title or self.video_id}"




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
	# Mark message to be shown on the public comment display
	display_selected = models.BooleanField(default=False)
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
