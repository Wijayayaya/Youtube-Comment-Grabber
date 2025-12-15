from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path("", views.LiveChatMessageListView.as_view(), name="message-list"),
    path("messages/<int:pk>/status/", views.update_message_status, name="message-status"),
    path("api/messages/", views.MessageListApiView.as_view(), name="messages-api"),
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
