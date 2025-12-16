from django.contrib import admin

from .models import LiveChatMessage, LiveStream, OBSConfig
from django.utils.html import format_html


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
	list_display = ('video_id', 'title', 'is_active', 'obs_config', 'last_polled_at', 'created_at')
	list_filter = ('is_active',)
	search_fields = ('video_id', 'title')


@admin.register(OBSConfig)
class OBSConfigAdmin(admin.ModelAdmin):
	list_display = ('name', 'host', 'port', 'default_text_source')
	search_fields = ('name', 'host')


@admin.register(LiveChatMessage)
class LiveChatMessageAdmin(admin.ModelAdmin):
	def author_avatar(self, obj):
		if obj.author_profile_image_url:
			return format_html('<img src="{}" style="width:36px;height:36px;border-radius:50%;" />', obj.author_profile_image_url)
		return ''

	author_avatar.short_description = 'Avatar'

	list_display = ('message_id', 'live_stream', 'author_avatar', 'author_name', 'obs_selected', 'status', 'published_at')
	list_filter = ('status', 'live_stream__video_id', 'obs_selected')
	search_fields = ('message_id', 'author_name', 'message_text')
	autocomplete_fields = ('live_stream',)

	actions = ['mark_selected_for_obs', 'unmark_selected_for_obs']

	def mark_selected_for_obs(self, request, queryset):
		updated = queryset.update(obs_selected=True)
		self.message_user(request, f"Marked {updated} message(s) for OBS display.")
	mark_selected_for_obs.short_description = 'Mark selected messages for OBS'

	def unmark_selected_for_obs(self, request, queryset):
		updated = queryset.update(obs_selected=False)
		self.message_user(request, f"Unmarked {updated} message(s) for OBS display.")
	unmark_selected_for_obs.short_description = 'Unmark selected messages for OBS'
