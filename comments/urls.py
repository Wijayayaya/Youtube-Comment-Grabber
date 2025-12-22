from django.urls import path
from django.views.generic import RedirectView

from . import views
from . import admin_views

app_name = "comments"

urlpatterns = [
    # Redirect root to admin dashboard
    path("", RedirectView.as_view(pattern_name='comments:admin-dashboard', permanent=False), name="root-redirect"),
    
    # Admin Dashboard Views (using admin_templates)
    path("admin/dashboard/", admin_views.admin_dashboard, name="admin-dashboard"),
    path("admin/livestreams/", admin_views.livestream_list, name="admin-livestream-list"),
    path("admin/livestreams/add/", admin_views.livestream_add, name="admin-livestream-add"),
    path("admin/livestreams/<int:pk>/edit/", admin_views.livestream_edit, name="admin-livestream-edit"),
    path("admin/livestreams/<int:pk>/delete/", admin_views.livestream_delete, name="admin-livestream-delete"),
    path("admin/messages/", admin_views.livechatmessage_list, name="admin-livechatmessage-list"),
    path("admin/messages/<int:pk>/", admin_views.livechatmessage_detail, name="admin-livechatmessage-detail"),
    path("admin/messages/bulk-action/", admin_views.livechatmessage_bulk_action, name="admin-livechatmessage-bulk-action"),
    
    # Original functionality (keeping URLs unchanged)
    path("messages/<int:pk>/status/", views.update_message_status, name="message-status"),
    path("display/", views.display, name="display"),
    path("manage/", views.manage_display, name="manage-display"),
    path("api/manage/messages/", views.manage_messages_api, name="manage-messages-api"),
    path("api/manage/reorder/", views.reorder_manage_api, name="manage-reorder-api"),
    path("api/manage/update_rotation/", views.update_rotation_api, name="manage-update-rotation"),
    path("api/messages/", views.MessageListApiView.as_view(), name="messages-api"),
    path("api/display_messages/", views.DisplayMessagesApiView.as_view(), name="display-messages-api"),
    path(
        "api/messages/<int:pk>/mark-sent/",
        views.mark_message_sent_api,
        name="message-mark-sent",
    ),
]
