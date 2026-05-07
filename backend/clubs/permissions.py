# clubs/permissions.py
# 行 1
from rest_framework import permissions
from .models import ClubMembership


class IsClubAdmin(permissions.BasePermission):
    """
    社团 owner/admin 才能做审批、管理板块等操作
    """
    def has_permission(self, request, view):
        club_id = view.kwargs.get("club_id") or request.data.get("club_id")
        if not request.user or not request.user.is_authenticated or not club_id:
            return False
        return ClubMembership.objects.filter(club_id=club_id, user=request.user, role__in=["owner", "admin"]).exists()
