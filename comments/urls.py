from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "comments"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name='admin:index', permanent=False), name="root-redirect"),
    path("messages/<int:pk>/status/", views.update_message_status, name="message-status"),
    path("obs/", views.obs_display, name="obs-display"),
    path("api/messages/", views.MessageListApiView.as_view(), name="messages-api"),
    path("api/obs_messages/", views.ObsMessagesApiView.as_view(), name="obs-messages-api"),
    path(
        "api/messages/<int:pk>/mark-sent/",
        views.mark_message_sent_api,
        name="message-mark-sent",
    ),
    path(
        "api/messages/<int:pk>/send-to-obs/",
        views.send_message_to_obs,
        name="message-send-to-obs",
    ),
]
