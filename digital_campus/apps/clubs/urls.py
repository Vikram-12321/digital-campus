from django.urls import path

from .views import (
    join_club, leave_club, ClubDetailView, toggle_featured          
)

urlpatterns = [
         
    path("clubs/<int:pk>/join/", join_club, name="club-join"),
    path("clubs/<int:pk>/leave/", leave_club, name="club-leave"),
    path("<slug:slug>/", ClubDetailView.as_view(), name="club-detail"),
    path("<slug:slug>/toggle-featured/", toggle_featured, name="toggle_featured"),

]