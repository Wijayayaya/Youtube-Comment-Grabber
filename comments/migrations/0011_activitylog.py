from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

	dependencies = [
		('comments', '0010_livestream_display_limit'),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='ActivityLog',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('action', models.CharField(db_index=True, max_length=64)),
				('details', models.JSONField(blank=True, default=dict)),
				('ip_address', models.GenericIPAddressField(blank=True, null=True)),
				('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
				('livestream', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to='comments.livestream')),
				('message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to='comments.livechatmessage')),
				('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to=settings.AUTH_USER_MODEL)),
			],
			options={
				'ordering': ['-created_at'],
			},
		),
	]
