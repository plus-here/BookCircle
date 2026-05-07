from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 第10-14行：列表页显示哪些列（可选，但很实用）
    list_display = ("username", "email", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)

    # 第18-20行：在原有用户字段基础上，追加你自定义的字段
    fieldsets = BaseUserAdmin.fieldsets + (
        ("扩展信息", {"fields": ("avatar", "bio")}),
    )
