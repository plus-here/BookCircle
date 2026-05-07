from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # 第7行：邮箱唯一（允许为空，避免旧数据迁移时出问题）
    email = models.EmailField(unique=True, null=True, blank=True)

    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username
