from django.contrib import admin

from .models import LiveChatMessage, LiveStream, OBSConfig


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
	list_display = ('message_id', 'live_stream', 'author_name', 'status', 'published_at')
	list_filter = ('status', 'live_stream__video_id')
	search_fields = ('message_id', 'author_name', 'message_text')
	autocomplete_fields = ('live_stream',)
