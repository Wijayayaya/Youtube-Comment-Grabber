from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from . import views
from . import admin_views

app_name = "comments"

urlpatterns = [
    # Admin Dashboard Views (using admin_templates) - MUST BE FIRST
    path("admin/login/", auth_views.LoginView.as_view(template_name='admin/login.html'), name="admin-login"),
    path("admin/logout/", auth_views.LogoutView.as_view(template_name='admin/logged_out.html', http_method_names=['get', 'post']), name="admin-logout"),
    path("admin/dashboard/", admin_views.admin_dashboard, name="admin-dashboard"),
    path("admin/livestreams/", admin_views.livestream_list, name="admin-livestream-list"),
    path("admin/livestreams/add/", admin_views.livestream_add, name="admin-livestream-add"),
    path("admin/livestreams/<int:pk>/edit/", admin_views.livestream_edit, name="admin-livestream-edit"),
    path("admin/livestreams/<int:pk>/delete/", admin_views.livestream_delete, name="admin-livestream-delete"),
    path("admin/messages/", admin_views.livechatmessage_list, name="admin-livechatmessage-list"),
    path("admin/messages/<int:pk>/", admin_views.livechatmessage_detail, name="admin-livechatmessage-detail"),
    path("admin/messages/bulk-action/", admin_views.livechatmessage_bulk_action, name="admin-livechatmessage-bulk-action"),
    
    # User Management Views
    path("admin/users/", admin_views.user_list, name="admin-user-list"),
    path("admin/users/add/", admin_views.user_add, name="admin-user-add"),
    path("admin/users/<int:pk>/edit/", admin_views.user_edit, name="admin-user-edit"),
    path("admin/users/<int:pk>/delete/", admin_views.user_delete, name="admin-user-delete"),
    path("admin/groups/", admin_views.group_list, name="admin-group-list"),
    path("admin/groups/add/", admin_views.group_add, name="admin-group-add"),
    path("admin/groups/<int:pk>/edit/", admin_views.group_edit, name="admin-group-edit"),
    path("admin/groups/<int:pk>/delete/", admin_views.group_delete, name="admin-group-delete"),
    
    # Profile & Password Views
    path("admin/profile/", admin_views.profile_view, name="admin-profile"),
    path("admin/change-password/", admin_views.change_password, name="admin-change-password"),
    
    # Redirect /admin/ to dashboard (after specific admin routes)
    path("admin/", RedirectView.as_view(pattern_name='comments:admin-dashboard', permanent=False), name="admin-redirect"),
    
    # Redirect root to admin dashboard
    path("", RedirectView.as_view(pattern_name='comments:admin-dashboard', permanent=False), name="root-redirect"),
    
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
