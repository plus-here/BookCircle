from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from clubs.models import ClubMembership
from .models import Activity, ActivitySignup
from .serializers import ActivitySerializer, ActivitySignupSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET",):
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class ActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = Activity.objects.all().prefetch_related("targets")
        # 只给普通用户看已发布
        if not (self.request.user and self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(status="published")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


from rest_framework import generics

class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Activity.objects.all().prefetch_related("targets")
    serializer_class = ActivitySerializer
    permission_classes = [IsStaffOrReadOnly]




class ActivitySignupView(APIView):
    """
    POST /api/activities/<id>/signup/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        act = Activity.objects.filter(id=pk).prefetch_related("targets").first()
        if not act:
            return Response({"detail": "活动不存在"}, status=status.HTTP_404_NOT_FOUND)

        if act.status != "published":
            return Response({"detail": "活动未发布"}, status=status.HTTP_400_BAD_REQUEST)

        if act.signup_deadline and timezone.now() > act.signup_deadline:
            return Response({"detail": "报名已截止"}, status=status.HTTP_400_BAD_REQUEST)

        # 用户必须属于活动分发的社团之一
        target_ids = list(act.targets.values_list("id", flat=True))
        if target_ids:
            m = ClubMembership.objects.filter(user=request.user, club_id__in=target_ids).first()
            if not m:
                return Response({"detail": "你不属于该活动分发的社团，无法报名"}, status=status.HTTP_403_FORBIDDEN)
            club_id = m.club_id
        else:
            # 如果没设置目标社团：先不允许（也可改成全站活动）
            return Response({"detail": "该活动未分发给任何社团"}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = ActivitySignup.objects.get_or_create(activity=act, user=request.user, defaults={"club_id": club_id})
        if not created and obj.status == "signed":
            return Response({"detail": "你已报名过"}, status=status.HTTP_400_BAD_REQUEST)
        if act.capacity and act.signups.filter(status="signed").count() >= act.capacity:
            return Response({"detail": "活动名额已满"}, status=status.HTTP_400_BAD_REQUEST)

        obj.status = "signed"
        obj.club_id = club_id
        obj.save()
        return Response(ActivitySignupSerializer(obj).data, status=status.HTTP_201_CREATED)


class ActivitySignupCancelView(APIView):
    """
    POST /api/activities/<id>/signup/cancel/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        obj = ActivitySignup.objects.filter(activity_id=pk, user=request.user).select_related(
            "activity", "club", "user"
        ).first()
        if not obj:
            return Response({"detail": "你还没有报名该活动"}, status=status.HTTP_404_NOT_FOUND)
        if obj.status == "cancelled":
            return Response({"detail": "报名已取消"}, status=status.HTTP_200_OK)

        obj.status = "cancelled"
        obj.save(update_fields=["status"])
        return Response(ActivitySignupSerializer(obj).data, status=status.HTTP_200_OK)


class MySignupsView(generics.ListAPIView):
    """
    GET /api/activities/my/signups/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivitySignupSerializer

    def get_queryset(self):
        return ActivitySignup.objects.filter(user=self.request.user, status="signed").select_related("activity", "club", "user")


class ActivitySignupsForClubAdminView(generics.ListAPIView):
    """
    GET /api/activities/<id>/signups/
    staff：看全部报名
    社团 owner/admin：只能看自己社团的报名
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivitySignupSerializer

    def get_queryset(self):
        act_id = self.kwargs["pk"]

        if self.request.user.is_staff:
            return ActivitySignup.objects.filter(activity_id=act_id).select_related("activity", "club", "user")

        # 不是 staff：只能看自己管理的社团报名
        admin_club_ids = ClubMembership.objects.filter(
            user=self.request.user, role__in=["owner", "admin"]
        ).values_list("club_id", flat=True)

        return ActivitySignup.objects.filter(activity_id=act_id, club_id__in=admin_club_ids).select_related("activity", "club", "user")
