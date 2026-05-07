from django.contrib import admin
from .models import ChatGroup, GroupMember, GroupMessage


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "creator", "is_public", "created_at")
    search_fields = ("name", "creator__username")


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "user", "role", "joined_at")
    search_fields = ("group__name", "user__username")


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "sender", "msg_type", "created_at")
    search_fields = ("group__name", "sender__username", "content")
