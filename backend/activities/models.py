from django.conf import settings
from django.db import models
from clubs.models import Club


class Activity(models.Model):
    STATUS_CHOICES = (
        ("draft", "草稿"),
        ("published", "已发布"),
        ("cancelled", "已取消"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    location = models.CharField(max_length=200, blank=True, default="")

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    signup_deadline = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField(default=0, help_text="0 means unlimited")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_activities")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    targets = models.ManyToManyField(Club, through="ActivityTargetClub", related_name="activities")

    class Meta:
        ordering = ["-start_time", "-id"]

    def __str__(self):
        return self.title


class ActivityTargetClub(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("activity", "club")

    def __str__(self):
        return f"{self.activity_id} -> {self.club_id}"


class ActivitySignup(models.Model):
    STATUS_CHOICES = (
        ("signed", "已报名"),
        ("cancelled", "已取消"),
    )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="signups")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="activity_signups")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_signups")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="signed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("activity", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id} signup {self.activity_id}"
