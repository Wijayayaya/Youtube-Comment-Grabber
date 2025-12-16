from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import LiveStream, LiveChatMessage


class ApiProfileImageTest(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user('staff', 'staff@example.com', 'pass')
		self.client.force_login(self.user)

		self.stream = LiveStream.objects.create(video_id='vid123', title='Test Stream')
		self.msg = LiveChatMessage.objects.create(
			live_stream=self.stream,
			message_id='msg1',
			author_name='Tester',
			author_channel_id='chan1',
			author_profile_image_url='https://example.com/avatar.png',
			message_text='hello world',
			published_at=timezone.now(),
		)

	def test_api_includes_profile_image(self):
		resp = self.client.get('/api/messages/?limit=10')
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		self.assertIn('messages', data)
		self.assertTrue(len(data['messages']) >= 1)
		self.assertEqual(data['messages'][0]['author_profile_image_url'], 'https://example.com/avatar.png')
