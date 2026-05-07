from django.conf import settings
from django.db import models


class DirectThread(models.Model):
    """
    私聊会话：两个人唯一对应一个 thread
    约定：user1_id < user2_id
    """
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dm_threads_as_user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dm_threads_as_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")
        ordering = ["-created_at"]

    def __str__(self):
        return f"DM({self.user1_id},{self.user2_id})"

    @staticmethod
    def normalize_pair(a_id: int, b_id: int):
        return (a_id, b_id) if a_id < b_id else (b_id, a_id)


class DirectMessage(models.Model):
    thread = models.ForeignKey(DirectThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dm_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"DM#{self.thread_id} by {self.sender_id}"
