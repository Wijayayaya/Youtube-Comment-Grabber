from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('comments', '0011_activitylog'),
	]

	operations = [
		migrations.CreateModel(
			name='CachedAvatar',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('name', models.CharField(max_length=120, unique=True)),
				('image', models.ImageField(upload_to='avatar_cache/')),
				('created_at', models.DateTimeField(auto_now_add=True)),
			],
			options={
				'ordering': ['-created_at'],
			},
		),
	]
