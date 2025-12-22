"""
Custom admin views using admin_templates (Datta Able) for YouTube Comment Grabber.
These views replace the default Django admin interface while maintaining all functionality.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import LiveStream, LiveChatMessage


@login_required(login_url='/admin/login/')
def admin_dashboard(request):
	"""Dashboard home with statistics."""
	total_streams = LiveStream.objects.count()
	active_streams = LiveStream.objects.filter(is_active=True).count()
	total_messages = LiveChatMessage.objects.count()
	
	# Status counts
	new_messages = LiveChatMessage.objects.filter(status='new').count()
	reviewed_messages = LiveChatMessage.objects.filter(status='reviewed').count()
	sent_messages = LiveChatMessage.objects.filter(status='sent').count()
	ignored_messages = LiveChatMessage.objects.filter(status='ignored').count()
	
	# Selected for display
	display_selected = LiveChatMessage.objects.filter(display_selected=True).count()
	
	# Recent messages
	recent_messages = LiveChatMessage.objects.select_related('live_stream').order_by('-published_at')[:10]
	
	# Recent streams
	recent_streams = LiveStream.objects.order_by('-created_at')[:5]
	
	context = {
		'total_streams': total_streams,
		'active_streams': active_streams,
		'total_messages': total_messages,
		'new_messages': new_messages,
		'reviewed_messages': reviewed_messages,
		'sent_messages': sent_messages,
		'ignored_messages': ignored_messages,
		'display_selected': display_selected,
		'recent_messages': recent_messages,
		'recent_streams': recent_streams,
	}
	
	return render(request, 'admin/dashboard.html', context)


@login_required(login_url='/admin/login/')
def livestream_list(request):
	"""List all live streams."""
	search_query = request.GET.get('search', '')
	is_active_filter = request.GET.get('is_active', '')
	
	streams = LiveStream.objects.all()
	
	if search_query:
		streams = streams.filter(
			Q(video_id__icontains=search_query) | 
			Q(title__icontains=search_query)
		)
	
	if is_active_filter:
		streams = streams.filter(is_active=(is_active_filter == 'true'))
	
	streams = streams.order_by('-created_at')
	
	# Pagination
	paginator = Paginator(streams, 20)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.get_page(page_number)
	
	context = {
		'page_obj': page_obj,
		'search_query': search_query,
		'is_active_filter': is_active_filter,
	}
	
	return render(request, 'admin/livestream_list.html', context)


@login_required(login_url='/admin/login/')
def livestream_add(request):
	"""Add new live stream."""
	if request.method == 'POST':
		video_id = request.POST.get('video_id', '').strip()
		title = request.POST.get('title', '').strip()
		is_active = request.POST.get('is_active') == 'on'
		display_rotation_seconds = request.POST.get('display_rotation_seconds', 6)
		
		if not video_id:
			messages.error(request, 'Video ID is required.')
			return render(request, 'admin/livestream_form.html')
		
		# Check if exists
		if LiveStream.objects.filter(video_id=video_id).exists():
			messages.error(request, f'Live stream with video ID "{video_id}" already exists.')
			return render(request, 'admin/livestream_form.html', {'video_id': video_id, 'title': title})
		
		LiveStream.objects.create(
			video_id=video_id,
			title=title,
			is_active=is_active,
			display_rotation_seconds=int(display_rotation_seconds)
		)
		
		messages.success(request, f'Live stream "{video_id}" added successfully.')
		return redirect('comments:admin-livestream-list')
	
	return render(request, 'admin/livestream_form.html')


@login_required(login_url='/admin/login/')
def livestream_edit(request, pk):
	"""Edit live stream."""
	stream = get_object_or_404(LiveStream, pk=pk)
	
	if request.method == 'POST':
		stream.video_id = request.POST.get('video_id', '').strip()
		stream.title = request.POST.get('title', '').strip()
		stream.is_active = request.POST.get('is_active') == 'on'
		stream.display_rotation_seconds = int(request.POST.get('display_rotation_seconds', 6))
		stream.save()
		
		messages.success(request, f'Live stream "{stream.video_id}" updated successfully.')
		return redirect('comments:admin-livestream-list')
	
	context = {'stream': stream}
	return render(request, 'admin/livestream_form.html', context)


@login_required(login_url='/admin/login/')
@require_POST
def livestream_delete(request, pk):
	"""Delete live stream."""
	stream = get_object_or_404(LiveStream, pk=pk)
	video_id = stream.video_id
	stream.delete()
	messages.success(request, f'Live stream "{video_id}" deleted successfully.')
	return redirect('comments:admin-livestream-list')


@login_required(login_url='/admin/login/')
def livechatmessage_list(request):
	"""List all live chat messages."""
	search_query = request.GET.get('search', '')
	status_filter = request.GET.get('status', '')
	stream_filter = request.GET.get('stream', '')
	display_filter = request.GET.get('display', '')
	
	messages_qs = LiveChatMessage.objects.select_related('live_stream').all()
	
	if search_query:
		messages_qs = messages_qs.filter(
			Q(message_id__icontains=search_query) | 
			Q(author_name__icontains=search_query) |
			Q(message_text__icontains=search_query)
		)
	
	if status_filter:
		messages_qs = messages_qs.filter(status=status_filter)
	
	if stream_filter:
		messages_qs = messages_qs.filter(live_stream__video_id=stream_filter)
	
	if display_filter:
		messages_qs = messages_qs.filter(display_selected=(display_filter == 'true'))
	
	messages_qs = messages_qs.order_by('-published_at')
	
	# Pagination
	paginator = Paginator(messages_qs, 30)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.get_page(page_number)
	
	# Get available streams for filter
	streams = LiveStream.objects.all().order_by('-created_at')
	
	context = {
		'page_obj': page_obj,
		'search_query': search_query,
		'status_filter': status_filter,
		'stream_filter': stream_filter,
		'display_filter': display_filter,
		'streams': streams,
		'status_choices': LiveChatMessage.Status.choices,
	}
	
	return render(request, 'admin/livechatmessage_list.html', context)


@login_required(login_url='/admin/login/')
def livechatmessage_detail(request, pk):
	"""View/Edit live chat message detail."""
	message = get_object_or_404(LiveChatMessage.objects.select_related('live_stream'), pk=pk)
	
	if request.method == 'POST':
		message.status = request.POST.get('status', message.status)
		message.note = request.POST.get('note', '')
		message.display_selected = request.POST.get('display_selected') == 'on'
		
		if message.status == LiveChatMessage.Status.SENT and not message.sent_at:
			message.sent_at = timezone.now()
		
		message.save()
		messages.success(request, f'Message from "{message.author_name}" updated successfully.')
		return redirect('comments:admin-livechatmessage-list')
	
	context = {
		'message': message,
		'status_choices': LiveChatMessage.Status.choices,
	}
	return render(request, 'admin/livechatmessage_detail.html', context)


@login_required(login_url='/admin/login/')
@require_POST
def livechatmessage_bulk_action(request):
	"""Bulk action for live chat messages."""
	action = request.POST.get('action')
	message_ids = request.POST.getlist('message_ids')
	
	if not message_ids:
		messages.warning(request, 'No messages selected.')
		return redirect('comments:admin-livechatmessage-list')
	
	messages_qs = LiveChatMessage.objects.filter(id__in=message_ids)
	count = messages_qs.count()
	
	if action == 'mark_display':
		messages_qs.update(display_selected=True)
		messages.success(request, f'{count} message(s) marked for display.')
	elif action == 'unmark_display':
		messages_qs.update(display_selected=False)
		messages.success(request, f'{count} message(s) unmarked for display.')
	elif action == 'mark_sent':
		messages_qs.update(status=LiveChatMessage.Status.SENT, sent_at=timezone.now())
		messages.success(request, f'{count} message(s) marked as sent.')
	elif action == 'mark_ignored':
		messages_qs.update(status=LiveChatMessage.Status.IGNORED)
		messages.success(request, f'{count} message(s) marked as ignored.')
	elif action == 'delete':
		messages_qs.delete()
		messages.success(request, f'{count} message(s) deleted.')
	else:
		messages.error(request, 'Unknown action.')
	
	return redirect('comments:admin-livechatmessage-list')
