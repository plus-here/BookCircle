# announcements/admin.py
# 行 1
from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_published", "published_at", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "content")
