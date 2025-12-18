from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "comments"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name='admin:index', permanent=False), name="root-redirect"),
    path("messages/<int:pk>/status/", views.update_message_status, name="message-status"),
    path("display/", views.display, name="display"),
    path("api/messages/", views.MessageListApiView.as_view(), name="messages-api"),
    path("api/display_messages/", views.DisplayMessagesApiView.as_view(), name="display-messages-api"),
    path(
        "api/messages/<int:pk>/mark-sent/",
        views.mark_message_sent_api,
        name="message-mark-sent",
    ),
    # OBS send endpoint removed; display management is handled via admin/actions and display API.
]
