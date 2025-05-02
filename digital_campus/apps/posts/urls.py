from django.urls import path, include
from .views import (
    PostDetailView, 
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    AttachmentDeleteView
)
from . import api_views

urlpatterns = [
    path("post/<int:pk>/", PostDetailView.as_view(), name='post-detail'), # pk := primary key for post
    path("post/new/", PostCreateView.as_view(), name='post-create'), 
    path("post/<int:pk>/update", PostUpdateView.as_view(), name='post-update'), 
    path("post/<int:pk>/delete", PostDeleteView.as_view(), name='post-delete'), 
    path('tinymce/', include('tinymce.urls')),
    #API View
    path('api/post/<int:pk>/', api_views.PostDetailView.as_view(), name='api-user-detail'),
    path(
        "attachment/<int:pk>/delete/",
        AttachmentDeleteView.as_view(),
        name="attachment-delete",
    ),
]