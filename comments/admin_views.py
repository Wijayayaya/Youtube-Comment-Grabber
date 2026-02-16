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
from django.contrib.auth.models import User, Group
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
import uuid

from .models import LiveStream, LiveChatMessage, ActivityLog, CachedAvatar
from .services.activity_log import log_activity


@login_required(login_url='/admin/login/')
def admin_dashboard(request):
	"""Dashboard home with statistics."""
	total_streams = LiveStream.objects.count()
	active_streams = LiveStream.objects.filter(is_active=True).count()
	total_messages = LiveChatMessage.objects.count()
	
	# Status counts (new_messages changed to 'today')
	new_messages = LiveChatMessage.objects.filter(published_at__date=timezone.now().date()).count()
	reviewed_messages = LiveChatMessage.objects.filter(status='reviewed').count()
	sent_messages = LiveChatMessage.objects.filter(status='sent').count()
	ignored_messages = LiveChatMessage.objects.filter(status='ignored').count()
	
	# Selected for display
	display_selected = LiveChatMessage.objects.filter(display_selected=True).count()
	
	# Recent messages
	recent_messages = LiveChatMessage.objects.select_related('live_stream').order_by('-published_at')[:10]
	
	# Recent streams
	recent_streams = LiveStream.objects.exclude(video_id='manual').order_by('-created_at')[:5]
	
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
	
	streams = LiveStream.objects.exclude(video_id='manual')
	
	if search_query:
		streams = streams.filter(
			Q(video_id__icontains=search_query) | 
			Q(title__icontains=search_query)
		)
	
	if is_active_filter:
		streams = streams.filter(is_active=(is_active_filter == 'true'))
	
	streams = streams.order_by('-created_at')
	
	# Return JSON if requested via AJAX
	if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
		streams_data = [
			{
				'id': s.id,
				'video_id': s.video_id,
				'title': s.title or s.video_id,
			}
			for s in streams
		]
		return JsonResponse({'streams': streams_data})
	
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
		display_rotation_seconds = request.POST.get('display_rotation_seconds', 15)
		
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
	stream_filter = request.GET.get('stream', '')
	display_filter = request.GET.get('display', '')
	start_date = request.GET.get('start_date', '')
	end_date = request.GET.get('end_date', '')
	
	messages_qs = LiveChatMessage.objects.select_related('live_stream').all()
	
	if search_query:
		messages_qs = messages_qs.filter(
			Q(message_id__icontains=search_query) | 
			Q(author_name__icontains=search_query) |
			Q(message_text__icontains=search_query)
		)
	
	if stream_filter:
		messages_qs = messages_qs.filter(live_stream__video_id=stream_filter)
	
	if display_filter:
		messages_qs = messages_qs.filter(display_selected=(display_filter == 'true'))

	if start_date and not end_date:
		messages_qs = messages_qs.filter(published_at__date=start_date)
	elif start_date and end_date:
		messages_qs = messages_qs.filter(published_at__date__gte=start_date, published_at__date__lte=end_date)
	elif not start_date and end_date:
		messages_qs = messages_qs.filter(published_at__date__lte=end_date)
	
	# Order by: pinned first (desc), then by published date (desc)
	messages_qs = messages_qs.order_by('-is_pinned', '-published_at')
	
	# Pagination
	paginator = Paginator(messages_qs, 30)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.get_page(page_number)
	
	# Get available streams for filter
	streams = LiveStream.objects.all().order_by('-created_at')
	
	context = {
		'page_obj': page_obj,
		'search_query': search_query,
		'stream_filter': stream_filter,
		'display_filter': display_filter,
		'start_date': start_date,
		'end_date': end_date,
		'streams': streams,
	}
	
	return render(request, 'admin/livechatmessage_list.html', context)


@login_required(login_url='/admin/login/')
def manual_message_create(request):
	"""Staff-only manual message input for display."""
	if not request.user.is_staff:
		raise PermissionDenied

	manual_stream, _created = LiveStream.objects.get_or_create(
		video_id='manual',
		defaults={
			'title': 'Manual Input',
			'is_active': False,
			'display_rotation_seconds': 15,
		},
	)
	latest_avatar = CachedAvatar.objects.order_by('-created_at').first()

	context = {
		'latest_avatar': latest_avatar,
	}

	if request.method == 'POST':
		author_name = request.POST.get('author_name', '').strip()
		message_text = request.POST.get('message_text', '').strip()
		avatar_file = request.FILES.get('avatar_file')

		context.update(
			{
				'author_name': author_name,
				'message_text': message_text,
				'has_avatar': bool(latest_avatar),
			}
		)

		if not author_name or not message_text:
			messages.error(request, 'Nama dan pesan wajib diisi.')
			return render(request, 'admin/manual_message_form.html', context)

		if not avatar_file and not latest_avatar:
			messages.error(request, 'Avatar wajib diisi. Upload avatar terlebih dahulu.')
			return render(request, 'admin/manual_message_form.html', context)

		avatar_url = ''
		new_avatar = None
		if avatar_file:
			# Keep old avatars - simpan avatar agar tetap tersimpan
			avatar_label = avatar_file.name or f"manual-avatar-{uuid.uuid4().hex[:6]}"
			if CachedAvatar.objects.filter(name=avatar_label).exists():
				avatar_label = f"{avatar_label}-{uuid.uuid4().hex[:6]}"
			new_avatar = CachedAvatar.objects.create(
				name=avatar_label,
				image=avatar_file,
			)
			avatar_url = new_avatar.image.url
		elif latest_avatar:
			avatar_url = latest_avatar.image.url

		message = LiveChatMessage.objects.create(
			live_stream=manual_stream,
			message_id=f"manual-{uuid.uuid4()}",
			author_name=author_name,
			author_channel_id='',
			author_profile_image_url=avatar_url,
			message_text=message_text,
			published_at=timezone.now(),
			display_selected=True,
			status=LiveChatMessage.Status.SENT,
			sent_at=timezone.now(),
		)

		from .services.display_limit import enforce_display_limit
		enforce_display_limit()

		log_activity(
			request,
			'manual_message_create',
			message=message,
			livestream=manual_stream,
			details={
				'avatar_cached': bool(new_avatar),
				'avatar_id': new_avatar.id if new_avatar else (latest_avatar.id if latest_avatar else None),
			},
		)

		messages.success(request, 'Komentar manual berhasil ditambahkan ke display.')
		return redirect('comments:admin-manual-message')

	return render(request, 'admin/manual_message_form.html', context)


@login_required(login_url='/admin/login/')
def livechatmessage_detail(request, pk):
	"""View/Edit live chat message detail."""
	message = get_object_or_404(LiveChatMessage.objects.select_related('live_stream'), pk=pk)
	
	if request.method == 'POST':
		print(f"DEBUG: Received POST for message {pk}: {request.POST}")
		updated_fields = ['updated_at']
		message.updated_at = timezone.now()
		previous_display_selected = message.display_selected
		previous_is_pinned = message.is_pinned
		display_changed = False
		pin_changed = False
		
		# Update only fields present in POST (essential for AJAX partial updates)
		if 'note' in request.POST:
			message.note = request.POST.get('note', '')
			updated_fields.append('note')
		
		# handle display_selected
		if 'display_selected' in request.POST:
			message.display_selected = request.POST.get('display_selected') == 'on'
			updated_fields.append('display_selected')
			print(f"DEBUG: Updating display_selected to {message.display_selected}")
			display_changed = message.display_selected != previous_display_selected
			
			if message.display_selected and not previous_display_selected:
				message.status = LiveChatMessage.Status.SENT
				message.sent_at = timezone.now()
				message.display_order = None  # Reset order so it jumps to 'new priority' pool
				updated_fields.extend(['status', 'sent_at', 'display_order'])
		
		# handle is_pinned
		if 'is_pinned' in request.POST:
			message.is_pinned = request.POST.get('is_pinned') == 'on'
			updated_fields.append('is_pinned')
			print(f"DEBUG: Updating is_pinned to {message.is_pinned}")
			pin_changed = message.is_pinned != previous_is_pinned
		
		# Use update_fields to prevent overwriting other fields (e.g. from background polling)
		print(f"DEBUG: Saving fields: {updated_fields}")
		message.save(update_fields=updated_fields)
		
		# Enforce display limit if message was newly selected
		removed_by_limit_ids = []
		if 'display_selected' in request.POST and message.display_selected and not previous_display_selected:
			from .services.display_limit import enforce_display_limit
			removed_by_limit_ids = enforce_display_limit()

		# Verify save
		message.refresh_from_db()
		print(f"DEBUG: Verified after save - Pinned: {message.is_pinned}, Display: {message.display_selected}")

		if display_changed:
			action = 'select_display' if message.display_selected else 'unselect_display'
			log_activity(
				request,
				action,
				message=message,
				livestream=message.live_stream,
				details={'source': 'single'},
			)

		if pin_changed:
			action = 'pin' if message.is_pinned else 'unpin'
			log_activity(
				request,
				action,
				message=message,
				livestream=message.live_stream,
				details={'source': 'single'},
			)
		
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return JsonResponse({
				'status': 'success',
				'message': f'Message from "{message.author_name}" updated successfully.',
				'is_pinned': message.is_pinned,
				'display_selected': message.display_selected,
				'display_limit_removed': len(removed_by_limit_ids),
				'display_limit_removed_ids': removed_by_limit_ids,
			})
			
		messages.success(request, f'Message from "{message.author_name}" updated successfully.')
		return redirect('comments:admin-livechatmessage-list')
	
	context = {
		'message': message,
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

	snapshots = []
	for msg in messages_qs.select_related('live_stream'):
		snapshots.append({
			'author_name': msg.author_name,
			'message_text': msg.message_text,
			'stream_title': msg.live_stream.title if msg.live_stream else None,
			'stream_video_id': msg.live_stream.video_id if msg.live_stream else None,
		})

	base_details = {'count': count, 'message_ids': message_ids}
	if snapshots:
		first = snapshots[0]
		base_details.update({
			'message_author': first.get('author_name'),
			'message_text': first.get('message_text'),
			'stream_title': first.get('stream_title'),
			'stream_video_id': first.get('stream_video_id'),
		})
		if count > 1:
			base_details['messages'] = snapshots[:3]
	
	if action == 'mark_display':
		messages_qs.update(display_selected=True)
		from .services.display_limit import enforce_display_limit
		removed_ids = enforce_display_limit()
		if removed_ids:
			messages.info(request, f'{len(removed_ids)} oldest message(s) removed from display due to limit.')
		messages.add_message(request, messages.SUCCESS, f'{count} message(s) marked for display.', extra_tags='success')
		details = {**base_details, 'removed_ids': removed_ids}
		log_activity(request, 'bulk_select_display', details=details)
	elif action == 'unmark_display':
		messages_qs.update(display_selected=False)
		messages.add_message(request, messages.INFO, f'{count} message(s) removed from display.', extra_tags='secondary')
		log_activity(request, 'bulk_unselect_display', details=base_details)
	elif action == 'pin_message':
		messages_qs.update(is_pinned=True)
		messages.add_message(request, messages.WARNING, f'{count} message(s) pinned.', extra_tags='warning')
		log_activity(request, 'bulk_pin', details=base_details)
	elif action == 'unpin_message':
		messages_qs.update(is_pinned=False)
		messages.add_message(request, messages.INFO, f'{count} message(s) unpinned.', extra_tags='secondary')
		log_activity(request, 'bulk_unpin', details=base_details)
	elif action == 'mark_sent':
		messages_qs.update(status=LiveChatMessage.Status.SENT, sent_at=timezone.now())
		messages.add_message(request, messages.INFO, f'{count} message(s) marked as sent.', extra_tags='info')
		log_activity(request, 'bulk_mark_sent', details=base_details)
	elif action == 'mark_ignored':
		messages_qs.update(status=LiveChatMessage.Status.IGNORED)
		messages.add_message(request, messages.INFO, f'{count} message(s) marked as ignored.', extra_tags='secondary')
		log_activity(request, 'bulk_mark_ignored', details=base_details)
	elif action == 'delete':
		details = base_details.copy()
		messages_qs.delete()
		messages.add_message(request, messages.ERROR, f'{count} message(s) deleted.', extra_tags='danger')
		log_activity(request, 'bulk_delete', details=details)
	else:
		messages.error(request, 'Unknown action.')
	
	return redirect('comments:admin-livechatmessage-list')


@login_required(login_url='/admin/login/')
def activity_log_list(request):
	"""List activity logs (superuser only)."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')

	search_query = request.GET.get('search', '')
	action_filter = request.GET.get('action', '')

	logs = ActivityLog.objects.select_related('user', 'message', 'livestream')

	if search_query:
		logs = logs.filter(
			Q(user__username__icontains=search_query) |
			Q(action__icontains=search_query) |
			Q(message__author_name__icontains=search_query) |
			Q(message__message_text__icontains=search_query) |
			Q(livestream__video_id__icontains=search_query)
		)

	if action_filter:
		logs = logs.filter(action=action_filter)

	actions = ActivityLog.objects.values_list('action', flat=True).distinct().order_by('action')

	logs = logs.order_by('-created_at')

	paginator = Paginator(logs, 50)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.get_page(page_number)

	context = {
		'page_obj': page_obj,
		'search_query': search_query,
		'action_filter': action_filter,
		'actions': actions,
	}

	return render(request, 'admin/activity_log.html', context)


@login_required(login_url='/admin/login/')
def activity_log_detail(request, pk):
	"""View activity log detail (superuser only)."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')

	log = get_object_or_404(ActivityLog.objects.select_related('user', 'message', 'livestream'), pk=pk)
	return render(request, 'admin/activity_log_detail.html', {'log': log})


@login_required(login_url='/admin/login/')
@require_POST
def activity_log_delete(request, pk):
	"""Delete activity log entry (superuser only)."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')

	log = get_object_or_404(ActivityLog, pk=pk)
	log.delete()
	messages.success(request, 'Activity log deleted.')
	return redirect('comments:admin-activity-log')


# ============================================
# USER MANAGEMENT VIEWS
# ============================================

@login_required(login_url='/admin/login/')
def user_list(request):
	"""List all users."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')
	
	search_query = request.GET.get('search', '')
	is_active_filter = request.GET.get('is_active', '')
	is_staff_filter = request.GET.get('is_staff', '')
	
	users = User.objects.all()
	
	if search_query:
		users = users.filter(
			Q(username__icontains=search_query) |
			Q(email__icontains=search_query) |
			Q(first_name__icontains=search_query) |
			Q(last_name__icontains=search_query)
		)
	
	if is_active_filter:
		users = users.filter(is_active=(is_active_filter == 'true'))
	
	if is_staff_filter:
		users = users.filter(is_staff=(is_staff_filter == 'true'))
	
	users = users.order_by('-date_joined')
	
	# Pagination
	paginator = Paginator(users, 20)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.get_page(page_number)
	
	context = {
		'page_obj': page_obj,
		'search_query': search_query,
		'is_active_filter': is_active_filter,
		'is_staff_filter': is_staff_filter,
	}
	
	return render(request, 'admin/user_list.html', context)


@login_required(login_url='/admin/login/')
def user_add(request):
	"""Add new user."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')
	
	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		email = request.POST.get('email', '').strip()
		password = request.POST.get('password', '')
		first_name = request.POST.get('first_name', '').strip()
		last_name = request.POST.get('last_name', '').strip()
		is_active = request.POST.get('is_active') == 'on'
		is_staff = request.POST.get('is_staff') == 'on'
		is_superuser = request.POST.get('is_superuser') == 'on'
		
		if not username:
			messages.error(request, 'Username is required.')
			return render(request, 'admin/user_form.html')
		
		if User.objects.filter(username=username).exists():
			messages.error(request, f'User with username "{username}" already exists.')
			return render(request, 'admin/user_form.html', {'username': username})
		
		user = User.objects.create_user(
			username=username,
			email=email,
			password=password,
			first_name=first_name,
			last_name=last_name,
			is_active=is_active,
			is_staff=is_staff,
			is_superuser=is_superuser
		)
		
		# Add to groups
		group_ids = request.POST.getlist('groups')
		if group_ids:
			user.groups.set(Group.objects.filter(id__in=group_ids))
		
		messages.success(request, f'User "{username}" added successfully.')
		return redirect('comments:admin-user-list')
	
	groups = Group.objects.all()
	context = {'groups': groups}
	return render(request, 'admin/user_form.html', context)


@login_required(login_url='/admin/login/')
def user_edit(request, pk):
	"""Edit user."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')
	
	user = get_object_or_404(User, pk=pk)
	
	if request.method == 'POST':
		user.username = request.POST.get('username', '').strip()
		user.email = request.POST.get('email', '').strip()
		user.first_name = request.POST.get('first_name', '').strip()
		user.last_name = request.POST.get('last_name', '').strip()
		user.is_active = request.POST.get('is_active') == 'on'
		user.is_staff = request.POST.get('is_staff') == 'on'
		user.is_superuser = request.POST.get('is_superuser') == 'on'
		
		# Change password if provided
		new_password = request.POST.get('password', '')
		if new_password:
			user.set_password(new_password)
		
		user.save()
		
		# Update groups
		group_ids = request.POST.getlist('groups')
		user.groups.set(Group.objects.filter(id__in=group_ids))
		
		messages.success(request, f'User "{user.username}" updated successfully.')
		return redirect('comments:admin-user-list')
	
	groups = Group.objects.all()
	context = {'user_obj': user, 'groups': groups}
	return render(request, 'admin/user_form.html', context)


@login_required(login_url='/admin/login/')
@require_POST
def user_delete(request, pk):
	"""Delete user."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to perform this action.')
		return redirect('comments:admin-dashboard')
	
	user = get_object_or_404(User, pk=pk)
	
	# Prevent deleting yourself
	if user.pk == request.user.pk:
		messages.error(request, 'You cannot delete your own account.')
		return redirect('comments:admin-user-list')
	
	username = user.username
	user.delete()
	messages.success(request, f'User "{username}" deleted successfully.')
	return redirect('comments:admin-user-list')


@login_required(login_url='/admin/login/')
def group_list(request):
	"""List all groups."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')
	
	search_query = request.GET.get('search', '')
	
	groups = Group.objects.annotate(user_count=Count('user')).all()
	
	if search_query:
		groups = groups.filter(name__icontains=search_query)
	
	groups = groups.order_by('name')
	
	# Pagination
	paginator = Paginator(groups, 20)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.get_page(page_number)
	
	context = {
		'page_obj': page_obj,
		'search_query': search_query,
	}
	
	return render(request, 'admin/group_list.html', context)


@login_required(login_url='/admin/login/')
def group_add(request):
	"""Add new group."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')
	
	if request.method == 'POST':
		name = request.POST.get('name', '').strip()
		
		if not name:
			messages.error(request, 'Group name is required.')
			return render(request, 'admin/group_form.html')
		
		if Group.objects.filter(name=name).exists():
			messages.error(request, f'Group with name "{name}" already exists.')
			return render(request, 'admin/group_form.html', {'name': name})
		
		Group.objects.create(name=name)
		
		messages.success(request, f'Group "{name}" added successfully.')
		return redirect('comments:admin-group-list')
	
	return render(request, 'admin/group_form.html')


@login_required(login_url='/admin/login/')
def group_edit(request, pk):
	"""Edit group."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to access this page.')
		return redirect('comments:admin-dashboard')
	
	group = get_object_or_404(Group, pk=pk)
	
	if request.method == 'POST':
		group.name = request.POST.get('name', '').strip()
		group.save()
		
		messages.success(request, f'Group "{group.name}" updated successfully.')
		return redirect('comments:admin-group-list')
	
	context = {'group': group}
	return render(request, 'admin/group_form.html', context)


@login_required(login_url='/admin/login/')
@require_POST
def group_delete(request, pk):
	"""Delete group."""
	if not request.user.is_superuser:
		messages.error(request, 'You do not have permission to perform this action.')
		return redirect('comments:admin-dashboard')
	
	group = get_object_or_404(Group, pk=pk)
	name = group.name
	group.delete()
	messages.success(request, f'Group "{name}" deleted successfully.')
	return redirect('comments:admin-group-list')


# ============================================
# PROFILE & PASSWORD VIEWS
# ============================================

@login_required(login_url='/admin/login/')
def profile_view(request):
	"""View user profile."""
	user = request.user
	
	if request.method == 'POST':
		user.first_name = request.POST.get('first_name', '').strip()
		user.last_name = request.POST.get('last_name', '').strip()
		user.email = request.POST.get('email', '').strip()
		user.save()
		
		messages.success(request, 'Profile updated successfully.')
		return redirect('comments:admin-profile')
	
	context = {'user': user}
	return render(request, 'admin/profile.html', context)


@login_required(login_url='/admin/login/')
def change_password(request):
	"""Change user password."""
	if request.method == 'POST':
		old_password = request.POST.get('old_password', '')
		new_password = request.POST.get('new_password1', '')
		confirm_password = request.POST.get('new_password2', '')
		
		# Validate old password
		if not request.user.check_password(old_password):
			messages.error(request, 'Old password is incorrect.')
			return render(request, 'admin/change_password.html')
		
		# Validate new password
		if len(new_password) < 8:
			messages.error(request, 'New password must be at least 8 characters long.')
			return render(request, 'admin/change_password.html')
		
		if new_password != confirm_password:
			messages.error(request, 'New passwords do not match.')
			return render(request, 'admin/change_password.html')
		
		# Change password
		request.user.set_password(new_password)
		request.user.save()
		
		# Keep user logged in after password change
		update_session_auth_hash(request, request.user)
		
		messages.success(request, 'Password changed successfully.')
		return redirect('comments:admin-dashboard')
	
	return render(request, 'admin/change_password.html')
