"""
apps/common/urls.py

URL configuration for the common app, handling:
- Post feeds
- User following and follow requests
- Search/autocomplete
- Notifications
- Static pages (about/account)
- API endpoint for course detail

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.urls import path, include

# Views
from .views import (
    CourseAutocomplete,
    about,
    account,
    notifications_list,
    dismiss_notification
)
from .additional_views.list_views import PostListView, UserPostListView
from .additional_views.search_views import search, autocomplete
from .additional_views.follow_views import (
    follow_user,
    unfollow_user,
    accept_follow_request,
    decline_follow_request,
    view_follow_requests,
)
from .api_views import CourseDetailView

app_name = 'common'

urlpatterns = [
    # ——— Feeds ———
    path("", PostListView.as_view(), name="digital-campus-app-home"),
    path("user/<str:username>/", UserPostListView.as_view(), name="user-posts"),

    # ——— Follow System ———
    path("user/<str:username>/follow/", follow_user, name="follow-user"),
    path("user/<str:username>/unfollow/", unfollow_user, name="unfollow-user"),
    path("follow-requests/", view_follow_requests, name="view-follow-requests"),
    path("follow-requests/accept/<int:request_profile_id>/", accept_follow_request, name="accept-follow-request"),
    path("follow-requests/decline/<int:request_profile_id>/", decline_follow_request, name="decline-follow-request"),

    # ——— Notifications ———
    path("notifications/", notifications_list, name="notifications"),
    path("notifications/dismiss/<int:pk>/", dismiss_notification, name="dismiss-notification"),

    # ——— Search + Autocomplete ———
    path("search/", search, name="search"),
    path("autocomplete/", autocomplete, name="autocomplete"),
    path("course-autocomplete/", CourseAutocomplete.as_view(), name="course-autocomplete"),

    # ——— Static Pages ———
    path("about/", about, name="digital-campus-app-about"),
    path("account/", account, name="digital-campus-app-account"),
    path("tinymce/", include("tinymce.urls")),

    # ——— API Endpoints ———
    path("api/digital_campus/<str:name>/", CourseDetailView.as_view(), name="api-course-detail"),
]
