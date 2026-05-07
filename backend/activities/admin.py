from django.contrib import admin
from .models import Activity, ActivityTargetClub, ActivitySignup


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "start_time", "end_time", "created_by")
    list_filter = ("status",)
    search_fields = ("title", "created_by__username")


@admin.register(ActivityTargetClub)
class ActivityTargetClubAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "club")


@admin.register(ActivitySignup)
class ActivitySignupAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "club", "user", "status", "created_at")
    list_filter = ("status", "club")
    search_fields = ("activity__title", "user__username")
