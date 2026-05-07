# clubs/admin.py
# 行 1
from django.contrib import admin
from .models import Club, ClubSection, ClubMembership, ClubJoinRequest, Post, Comment


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("name", "owner__username")


@admin.register(ClubSection)
class ClubSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "club", "name", "order")
    list_filter = ("club",)
    ordering = ("club", "order")


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "club", "user", "role", "joined_at")
    list_filter = ("club", "role")
    search_fields = ("club__name", "user__username")


@admin.register(ClubJoinRequest)
class ClubJoinRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "club", "user", "status", "created_at", "reviewed_at", "reviewed_by")
    list_filter = ("status", "club")
    search_fields = ("club__name", "user__username")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "club", "section", "author", "title", "is_pinned", "created_at")
    list_filter = ("club", "section", "is_pinned")
    search_fields = ("title", "author__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    search_fields = ("post__title", "author__username")
