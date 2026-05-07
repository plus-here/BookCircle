# announcements/models.py
# 行 1
from django.conf import settings
from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    title = models.CharField(max_length=200)              # 行 8
    content = models.TextField()                          # 行 9

    is_published = models.BooleanField(default=False)     # 行 11
    published_at = models.DateTimeField(null=True, blank=True)  # 行 12

    created_by = models.ForeignKey(                       # 行 14
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="announcements",
    )

    created_at = models.DateTimeField(auto_now_add=True)  # 行 23
    updated_at = models.DateTimeField(auto_now=True)      # 行 24

    def save(self, *args, **kwargs):                      # 行 26
        # 如果发布了但没有发布时间，就补一个
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:                                           # 行 33
        ordering = ["-published_at", "-created_at"]

    def __str__(self):                                    # 行 36
        return self.title
