# clubs/models.py
# 行 1
from django.conf import settings
from django.db import models


# 行 6
class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 行 7
    description = models.TextField(blank=True, default="")  # 行 8

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_clubs")  # 行 10
    created_at = models.DateTimeField(auto_now_add=True)  # 行 11
    updated_at = models.DateTimeField(auto_now=True)  # 行 12

    def __str__(self):  # 行 14
        return self.name


# 行 18
class ClubSection(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="sections")  # 行 19
    name = models.CharField(max_length=100)  # 行 20
    order = models.PositiveIntegerField(default=1)  # 行 21

    class Meta:  # 行 23
        unique_together = ("club", "name")
        ordering = ["order", "id"]

    def __str__(self):  # 行 28
        return f"{self.club.name} / {self.name}"


# 行 32
class ClubMembership(models.Model):
    ROLE_CHOICES = (
        ("owner", "社团团长"),
        ("admin", "管理员"),
        ("member", "成员"),
    )

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="memberships")  # 行 41
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="club_memberships")  # 行 42
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")  # 行 43
    joined_at = models.DateTimeField(auto_now_add=True)  # 行 44

    class Meta:  # 行 46
        unique_together = ("club", "user")

    def __str__(self):  # 行 50
        return f"{self.user.username} in {self.club.name} ({self.role})"


# 行 54
class ClubJoinRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "待审批"),
        ("approved", "已通过"),
        ("rejected", "已拒绝"),
    )

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="join_requests")  # 行 64
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="club_join_requests")  # 行 65
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")  # 行 66
    reason = models.CharField(max_length=255, blank=True, default="")  # 行 67
    created_at = models.DateTimeField(auto_now_add=True)  # 行 68
    reviewed_at = models.DateTimeField(null=True, blank=True)  # 行 69
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_join_requests"
    )  # 行 72

    class Meta:  # 行 74
        unique_together = ("club", "user")
        ordering = ["-created_at"]

    def __str__(self):  # 行 79
        return f"{self.user.username} -> {self.club.name} ({self.status})"


# 行 83
class Post(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="posts")  # 行 84
    section = models.ForeignKey(ClubSection, on_delete=models.CASCADE, related_name="posts")  # 行 85
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")  # 行 86

    title = models.CharField(max_length=200)  # 行 88
    content = models.TextField()  # 行 89
    is_pinned = models.BooleanField(default=False)  # 行 90

    created_at = models.DateTimeField(auto_now_add=True)  # 行 92
    updated_at = models.DateTimeField(auto_now=True)  # 行 93

    class Meta:  # 行 95
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):  # 行 99
        return self.title


# 行 103
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")  # 行 104
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")  # 行 105
    content = models.TextField()  # 行 106
    created_at = models.DateTimeField(auto_now_add=True)  # 行 107

    class Meta:  # 行 109
        ordering = ["created_at"]

    def __str__(self):  # 行 113
        return f"Comment by {self.author.username}"

# ===== 在 clubs/models.py 文件最底部追加 =====
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Club)
def ensure_owner_membership(sender, instance: Club, created: bool, **kwargs):
    """
    确保 Club.owner 一定在 ClubMembership 里有一条 role='owner' 的记录
    否则团长会被系统当成“不是管理员”，导致无法审批/管理等
    """
    if not instance.owner_id:
        return

    # 1) 给团长补一条 membership（没有就创建，有就更新为 owner）
    ClubMembership.objects.update_or_create(
        club=instance,
        user_id=instance.owner_id,
        defaults={"role": "owner"},
    )

    # 2) 可选：如果历史上出现多个 owner，把其它 owner 降级为 admin
    ClubMembership.objects.filter(club=instance, role="owner") \
        .exclude(user_id=instance.owner_id) \
        .update(role="admin")
