# groupchat/models.py
from django.conf import settings
from django.db import models


class ChatGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, default="")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_groups")
    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    ROLE_CHOICES = (
        ("owner", "群主"),
        ("member", "成员"),
    )

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "user")

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class GroupMessage(models.Model):
    TYPE_CHOICES = (
        ("text", "文本"),
    )

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_group_messages")
    msg_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="text")
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.group_id} - {self.sender_id}"
