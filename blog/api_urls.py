from django.urls import path
from .api_views import (
    PostListCreateAPIView,
    PostRetrieveUpdateDestroyAPIView,
    CommentListCreateAPIView,
)

urlpatterns = [
    path("posts/", PostListCreateAPIView.as_view(), name="api-post-list"),
    path("posts/<int:pk>/", PostRetrieveUpdateDestroyAPIView.as_view(), name="api-post-detail"),
    path("posts/<int:pk>/comments/", CommentListCreateAPIView.as_view(), name="api-post-comments"),
]
