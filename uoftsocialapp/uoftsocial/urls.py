from django.urls import path, include
from .views import (
    PostListView, 
    UserPostListView,
    CourseAutocomplete,
)

from . import views


urlpatterns = [
    path("", PostListView.as_view(), name='uoft-social-app-home'),
    path("user/<str:username>/", UserPostListView.as_view(), name='user-posts'),
    path('user/<str:username>/follow/', views.follow_user, name='follow-user'),
    # Follow/unfollow
    path('user/<str:username>/follow/', views.follow_user, name='follow-user'),
    path('user/<str:username>/unfollow/', views.unfollow_user, name='unfollow-user'),

    # Accept/decline follow requests
    path('follow-requests/accept/<int:request_profile_id>/', views.accept_follow_request, name='accept-follow-request'),
    path('follow-requests/decline/<int:request_profile_id>/', views.decline_follow_request, name='decline-follow-request'),\
    path('follow-requests/', views.view_follow_requests, name='view-follow-requests'),

    path('course-autocomplete/', CourseAutocomplete.as_view(), name='course-autocomplete'),
    path("about/", views.about, name='uoft-social-app-about'),
    path("account/", views.account, name='uoft-social-app-account'),
    path('tinymce/', include('tinymce.urls')),

    path('posts/', include(('posts.urls', 'posts'), namespace='posts')),  

    path('search/', views.search, name='search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),


]