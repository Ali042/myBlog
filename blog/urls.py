from django.urls import path
from . import views
 
urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/<int:pk>/like/", views.like_toggle, name="like_toggle"),
    path("post/new/", views.post_create, name="post_create"),
    path("random/", views.post_random, name="post_random"),
    path("profile/", views.profile_view, name="profile"),
    path("u/<str:username>/", views.profile_user_view, name="profile_user"),
    path("u/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("u/<str:username>/followers/", views.followers_list, name="followers_list"),
    path("u/<str:username>/following/", views.following_list, name="following_list"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]
