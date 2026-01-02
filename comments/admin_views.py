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
	stream_filter = request.GET.get('stream', '')
	display_filter = request.GET.get('display', '')
	
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
		'stream_filter': stream_filter,
		'display_filter': display_filter,
		'streams': streams,
	}
	
	return render(request, 'admin/livechatmessage_list.html', context)


@login_required(login_url='/admin/login/')
def livechatmessage_detail(request, pk):
	"""View/Edit live chat message detail."""
	message = get_object_or_404(LiveChatMessage.objects.select_related('live_stream'), pk=pk)
	
	if request.method == 'POST':
		message.note = request.POST.get('note', '')
		previous_display_selected = message.display_selected
		message.display_selected = request.POST.get('display_selected') == 'on'
		
		if message.display_selected and not previous_display_selected:
			message.status = LiveChatMessage.Status.SENT
			if not message.sent_at:
				message.sent_at = timezone.now()
		
		message.save()
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
