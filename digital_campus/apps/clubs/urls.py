from django.urls import path

from .views import (
    ClubDetailView, ToggleFeaturedView, ToggleMembershipView, UserClubsView, ClubCreateView, ClubSettingsView, DeleteClubView      
)

urlpatterns = [
    path("club/<slug:slug>/", ClubDetailView.as_view(), name="club-detail"),
    path("<slug:slug>/toggle-featured/", ToggleFeaturedView.as_view(), name="toggle_featured"),
    path('<slug:slug>/membership/', ToggleMembershipView.as_view(), name='toggle-membership'),
    path('your-clubs/', UserClubsView.as_view(), name='user-clubs'),
    path("new/", ClubCreateView.as_view(), name="club-create"),
    path('<slug:slug>/settings/', ClubSettingsView.as_view(), name='club-settings'),
    path('<slug:slug>/delete/', DeleteClubView.as_view(), name='club-delete'),
]