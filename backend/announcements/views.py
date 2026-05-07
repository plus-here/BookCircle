from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from books.models import Book, Chapter, Bookshelf
from .models import Announcement
from .serializers import (
    AnnouncementListSerializer,
    AnnouncementDetailSerializer,
    AnnouncementAdminSerializer,
)


# ===== 用户端：只看已发布 =====
class AnnouncementPublicListView(generics.ListAPIView):
    serializer_class = AnnouncementListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Announcement.objects.filter(is_published=True)


class AnnouncementPublicDetailView(generics.RetrieveAPIView):
    serializer_class = AnnouncementDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Announcement.objects.filter(is_published=True)


# ===== 管理端：staff 可增删改查全部 =====
class AnnouncementAdminListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementAdminSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Announcement.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AnnouncementAdminRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnouncementAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Announcement.objects.all()


# ===== 管理端：统计大盘 =====
class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = timezone.localdate()
        start = today - timedelta(days=13)  # 近 14 天（含今天）

        # 预置日期轴
        axis = [start + timedelta(days=i) for i in range(14)]
        axis_map = {d: 0 for d in axis}

        def build_series(qs):
            m = dict(axis_map)
            for row in qs:
                d = row["d"]
                if d in m:
                    m[d] = row["c"]
            return [{"date": d.isoformat(), "count": m[d]} for d in axis]

        ann_total = Announcement.objects.count()
        ann_published = Announcement.objects.filter(is_published=True).count()

        ann_pub_daily_qs = (
            Announcement.objects.filter(is_published=True, published_at__date__gte=start)
            .annotate(d=TruncDate("published_at"))
            .values("d")
            .annotate(c=Count("id"))
        )

        shelf_daily_qs = (
            Bookshelf.objects.filter(added_at__date__gte=start)
            .annotate(d=TruncDate("added_at"))
            .values("d")
            .annotate(c=Count("id"))
        )

        user_daily_qs = (
            User.objects.filter(created_at__date__gte=start)
            .annotate(d=TruncDate("created_at"))
            .values("d")
            .annotate(c=Count("id"))
        )

        latest_ann = list(
            Announcement.objects.order_by("-created_at")
            .values("id", "title", "is_published", "published_at", "created_at")[:6]
        )

        data = {
            "counts": {
                "users": User.objects.count(),
                "books": Book.objects.count(),
                "chapters": Chapter.objects.count(),
                "shelf_items": Bookshelf.objects.count(),
                "announcements_total": ann_total,
                "announcements_published": ann_published,
                "announcements_draft": ann_total - ann_published,
            },
            "series": {
                "announcements_published_14d": build_series(ann_pub_daily_qs),
                "shelf_added_14d": build_series(shelf_daily_qs),
                "users_new_14d": build_series(user_daily_qs),
            },
            "latest": {
                "announcements": latest_ann,
            },
        }
        return Response(data)

from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
import os, uuid

class AdminUploadView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "file is required"}, status=400)

        # 只允许图片
        ct = getattr(f, "content_type", "") or ""
        if not ct.startswith("image/"):
            return Response({"detail": "only image files allowed"}, status=400)

        # 限制 5MB（可自行改）
        if f.size and f.size > 5 * 1024 * 1024:
            return Response({"detail": "file too large (max 5MB)"}, status=400)

        ext = os.path.splitext(f.name)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            return Response({"detail": "unsupported image type"}, status=400)

        filename = f"{uuid.uuid4().hex}{ext}"
        path = f"announcement_uploads/{filename}"

        saved_path = default_storage.save(path, f)
        url = default_storage.url(saved_path)  # /media/...
        abs_url = request.build_absolute_uri(url)

        return Response({"url": abs_url})
