"""
apps/common/urls.py

URL configuration for the `common` app, handling:
- Post feeds
- Static info pages
- API endpoint for course detail

Author: Vikram Bhojanala
Last updated: 2025-05-09
"""

from django.urls import path, include

# Core Views
from .views import (
    about,
    account,
    CourseAutocomplete,
)

# Modular Views
from .additional_views.list_views import PostListView, UserPostListView

from .api_views import CourseDetailView

app_name = "common"

urlpatterns = [
    # ——— Feeds ———
    path("", PostListView.as_view(), name="digital-campus-app-home"),
    path("user/<str:username>/", UserPostListView.as_view(), name="user-posts"),

    # -- Courses ----
    path("course-autocomplete/", CourseAutocomplete.as_view(), name="course-autocomplete"),

    # ——— Static Pages ———
    path("about/", about, name="digital-campus-app-about"),
    path("account/", account, name="digital-campus-app-account"),
    path("tinymce/", include("tinymce.urls")),

    # ——— API ———
    path("api/digital_campus/<str:name>/", CourseDetailView.as_view(), name="api-course-detail"),
]
