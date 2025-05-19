from django.urls import path
from .views import follow_user, unfollow_user, view_follow_requests, accept_follow_request, decline_follow_request

app_name = "connections"

urlpatterns = [
    path("user/<str:username>/follow/",   follow_user,   name="follow-user"),
    path("user/<str:username>/unfollow/", unfollow_user, name="unfollow-user"),

    path("follow-requests/",                                 view_follow_requests,  name="view-follow-requests"),
    path("follow-requests/accept/<int:request_profile_id>/", accept_follow_request, name="accept-follow-request"),
    path("follow-requests/decline/<int:request_profile_id>/",decline_follow_request,name="decline-follow-request"),
]
