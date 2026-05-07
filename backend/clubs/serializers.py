# clubs/serializers.py
from rest_framework import serializers
from .models import Club, ClubSection, ClubJoinRequest, Post, Comment, ClubMembership


class ClubListSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source="memberships.count", read_only=True)
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Club
        fields = ["id", "name", "description", "owner", "owner_username", "members_count", "created_at"]
        read_only_fields = ["id", "owner", "owner_username", "members_count", "created_at"]


class ClubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubSection
        fields = ["id", "club", "name", "order"]


class JoinRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubJoinRequest
        fields = ["club", "reason"]


class JoinRequestSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ClubJoinRequest
        fields = ["id", "club", "user", "user_username", "status", "reason", "created_at", "reviewed_at", "reviewed_by"]


class PostListSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "club",
            "section",
            "author",
            "author_username",
            "title",
            "is_pinned",
            "created_at",
            "comments_count",
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "club",
            "section",
            "author",
            "author_username",
            "title",
            "content",
            "is_pinned",
            "created_at",
            "updated_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "author_username", "content", "created_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ClubMembership
        fields = ["id", "club", "user", "user_username", "role", "joined_at"]


class PostCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, allow_blank=False, trim_whitespace=True)
    content = serializers.CharField(allow_blank=False, trim_whitespace=True)


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=False, trim_whitespace=True)
