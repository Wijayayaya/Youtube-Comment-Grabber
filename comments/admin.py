from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html

from .models import LiveChatMessage, LiveStream, ManageableLiveChatMessage


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
	list_display = ('video_id', 'title', 'is_active', 'display_rotation_seconds', 'last_polled_at', 'created_at')
	list_editable = ('display_rotation_seconds',)
	list_display_links = ('video_id',)
	list_filter = ('is_active',)
	search_fields = ('video_id', 'title')




@admin.register(LiveChatMessage)
class LiveChatMessageAdmin(admin.ModelAdmin):
	def author_avatar(self, obj):
		if obj.author_profile_image_url:
			return format_html('<img src="{}" style="width:36px;height:36px;border-radius:50%;" />', obj.author_profile_image_url)
		return ''

	author_avatar.short_description = 'Avatar'

	def full_message(self, obj):
		return obj.message_text

	full_message.short_description = 'Message'

	list_display = ('message_id', 'live_stream', 'author_avatar', 'author_name', 'full_message', 'display_selected', 'status', 'published_at')
	list_filter = ('status', 'live_stream__video_id', 'display_selected')
	list_editable = ('display_selected',)
	list_display_links = ('message_id',)
	search_fields = ('message_id', 'author_name', 'message_text')
	autocomplete_fields = ('live_stream',)

	actions = ['mark_selected_for_display', 'unmark_selected_for_display']

	def mark_selected_for_display(self, request, queryset):
		updated = queryset.update(display_selected=True)
		self.message_user(request, f"Marked {updated} message(s) for display.")
	mark_selected_for_display.short_description = 'Mark selected messages for display'

	def unmark_selected_for_display(self, request, queryset):
		updated = queryset.update(display_selected=False)
		self.message_user(request, f"Unmarked {updated} message(s) for display.")
	unmark_selected_for_display.short_description = 'Unmark selected messages for display'


@admin.register(ManageableLiveChatMessage)
class ManageableLiveChatMessageAdmin(admin.ModelAdmin):
	"""Proxy entry that redirects to the custom manage-comment screen."""

	change_list_template = 'comments/manage_display.html'

	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		return request.user.has_perm('comments.change_livechatmessage')

	def has_delete_permission(self, request, obj=None):
		return False

	def changelist_view(self, request, extra_context=None):
		"""Provide a custom page title so the admin change-list shows the desired label."""
		extra_context = extra_context or {}
		extra_context.setdefault('title', 'Manage live chat')

		# Provide current rotation seconds (take the first stream as representative)
		from .models import LiveStream
		first = LiveStream.objects.order_by('-created_at').first()
		if first:
			extra_context.setdefault('current_rotation_seconds', first.display_rotation_seconds)
		else:
			extra_context.setdefault('current_rotation_seconds', '')

		return super().changelist_view(request, extra_context=extra_context)
