from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils.http import urlencode
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import LiveChatMessage
from .services.obs import send_text_to_obs


def obs_display(request):
	"""Public minimal page for OBS browser source. Shows selected messages in a loop."""
	return render(request, 'comments/obs_display.html')


class ObsMessagesApiView(View):
	"""Public API returning messages marked for OBS display."""
	def get(self, request):
		queryset = (
			LiveChatMessage.objects.filter(obs_selected=True)
			.select_related('live_stream')
			.order_by('published_at')
		)

		data = [
			{
				'id': m.id,
				'author_name': m.author_name,
				'author_profile_image_url': m.author_profile_image_url or None,
				'text': m.message_text,
			}
			for m in queryset
		]

		return JsonResponse({'messages': data})


@login_required(login_url='/admin/login/')
@require_POST
def update_message_status(request, pk):
	message = get_object_or_404(LiveChatMessage, pk=pk)
	new_status = request.POST.get('status')
	note = request.POST.get('note', '').strip()

	if new_status not in dict(LiveChatMessage.Status.choices):
		return HttpResponseBadRequest('Status tidak dikenal.')

	if new_status == LiveChatMessage.Status.SENT:
		message.mark_sent(note=note)
	else:
		message.status = new_status
		message.note = note
		message.save(update_fields=['status', 'note', 'updated_at'])

	return redirect('admin:comments_livechatmessage_changelist')


@method_decorator(login_required(login_url='/admin/login/'), name='dispatch')
class MessageListApiView(View):
	def get(self, request):
		queryset = LiveChatMessage.objects.select_related('live_stream')

		status_param = request.GET.get('status')
		video_id = request.GET.get('video_id')
		since = request.GET.get('since')
		limit = min(500, int(request.GET.get('limit', 100)))

		if status_param:
			queryset = queryset.filter(status=status_param)
		if video_id:
			queryset = queryset.filter(live_stream__video_id__iexact=video_id)
		if since:
			parsed = parse_datetime(since)
			if parsed:
				queryset = queryset.filter(updated_at__gte=parsed)

		queryset = queryset.order_by('-published_at')[:limit]

		data = [
			{
				'id': message.id,
				'message_id': message.message_id,
				'video_id': message.live_stream.video_id,
				'author': message.author_name,
				'author_profile_image_url': message.author_profile_image_url or None,
				'text': message.message_text,
				'status': message.status,
				'note': message.note,
				'published_at': message.published_at.isoformat(),
				'sent_at': message.sent_at.isoformat() if message.sent_at else None,
			}
			for message in queryset
		]

		return JsonResponse({'messages': data})


@login_required(login_url='/admin/login/')
@require_POST
def mark_message_sent_api(request, pk):
	message = get_object_or_404(LiveChatMessage, pk=pk)
	note = request.POST.get('note')
	message.mark_sent(note=note)
	# Optionally send message to OBS if stream has OBS configured
	stream = message.live_stream
	sent_to_obs = False
	cfg = getattr(stream, 'obs_config', None)
	if cfg and cfg.host and cfg.port and (cfg.default_text_source or stream.obs_config.default_text_source):
		source = stream.obs_config.default_text_source or cfg.default_text_source
		text = f"{message.author_name}: {message.message_text}"
		sent_to_obs = send_text_to_obs(cfg.host, cfg.port, cfg.password, source, text)

	return JsonResponse({'status': 'ok', 'id': message.id, 'sent_to_obs': sent_to_obs})


@login_required(login_url='/admin/login/')
@require_POST
def send_message_to_obs(request, pk):
	"""Send a single LiveChatMessage to OBS without changing its status.

	Expects CSRF token for POST from the dashboard.
	"""
	message = get_object_or_404(LiveChatMessage, pk=pk)
	stream = message.live_stream
	cfg = getattr(stream, 'obs_config', None)
	if not cfg or not (cfg.host and cfg.port and (cfg.default_text_source or cfg.default_text_source)):
		return JsonResponse({'status': 'error', 'message': 'OBS not configured for this stream.'}, status=400)

	source = cfg.default_text_source
	text = f"{message.author_name}: {message.message_text}"
	success = send_text_to_obs(cfg.host, cfg.port, cfg.password, source, text)
	if success:
		return JsonResponse({'status': 'ok', 'sent_to_obs': True})
	return JsonResponse({'status': 'error', 'sent_to_obs': False}, status=500)

# Create your views here.
