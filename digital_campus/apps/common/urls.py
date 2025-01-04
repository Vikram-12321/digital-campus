from django.urls import path, include

from .additional_views.list_views import (
    PostListView,
    UserPostListView,
)
from .additional_views.search_views import search, autocomplete
from .additional_views.follow_views import Follow
from .views import CourseAutocomplete, about, account
from .api_views import CourseDetailView
from apps import posts

urlpatterns = [
    path("", PostListView.as_view(), name='digital-campus-app-home'),
    path("user/<str:username>/", UserPostListView.as_view(), name='user-posts'),
    path('user/<str:username>/follow/', Follow.follow_user, name='follow-user'),
    # Follow/unfollow
    path('user/<str:username>/follow/', Follow.follow_user, name='follow-user'),
    path('user/<str:username>/unfollow/', Follow.unfollow_user, name='unfollow-user'),

    # Accept/decline follow requests
    path('follow-requests/accept/<int:request_profile_id>/', Follow.accept_follow_request, name='accept-follow-request'),
    path('follow-requests/decline/<int:request_profile_id>/', Follow.decline_follow_request, name='decline-follow-request'),\
    path('follow-requests/', Follow.view_follow_requests, name='view-follow-requests'),

    path('course-autocomplete/', CourseAutocomplete.as_view(), name='course-autocomplete'),
    path("about/", about, name='digital-campus-app-about'),
    path("account/", account, name='digital-campus-app-account'),
    path('tinymce/', include('tinymce.urls')),

    path('search/', search, name='search'),
    path('autocomplete/', autocomplete, name='autocomplete'),

    #API Endpoint
    path('api/digital_campus/<str:name>/', CourseDetailView.as_view(), name='api-course-detail'),


]