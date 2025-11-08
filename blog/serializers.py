from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Profile, Like, Follow

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "content", "created_at"]
        read_only_fields = ["author", "created_at", "post"]

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user", "display_name", "bio", "website", "avatar"]


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    target = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "user", "target", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ["id", "title", "content", "image", "author", "created_at", "comments"]
        read_only_fields = ["author", "created_at"]
