from django.db import migrations
from django.utils import timezone


def unselect_over_200_display_messages(apps, schema_editor):
    LiveChatMessage = apps.get_model('comments', 'LiveChatMessage')

    for message in LiveChatMessage.objects.filter(display_selected=True).iterator():
        if len((message.message_text or '')) <= 200:
            continue

        message.display_selected = False
        message.is_pinned = False
        message.display_order = None
        message.updated_at = timezone.now()
        message.save(update_fields=['display_selected', 'is_pinned', 'display_order', 'updated_at'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0012_cachedavatar'),
    ]

    operations = [
        migrations.RunPython(unselect_over_200_display_messages, noop_reverse),
    ]
