from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Post, Comment, Profile, Follow
from .serializers import PostSerializer, CommentSerializer, UserSerializer, ProfileSerializer, FollowSerializer

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class PostListCreateAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if self.request.user != self.get_object().author:
            raise permissions.PermissionDenied("You cannot edit this post.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise permissions.PermissionDenied("You cannot delete this post.")
        instance.delete()

class FollowToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        target_user_id = self.kwargs.get("pk")
        target_user = get_object_or_404(User, pk=target_user_id)
        user = request.user

        if user == target_user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            follow = Follow.objects.get(user=user, target=target_user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            follow = Follow.objects.create(user=user, target=target_user)
            serializer = FollowSerializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs["pk"]
        return Comment.objects.filter(post__id=post_id).order_by("created_at")

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        serializer.save(author=self.request.user, post=post)
