from django.db.models import Q
from rest_framework import generics, permissions

from .models import Club, ClubSection, ClubJoinRequest
from .serializers import ClubListSerializer, ClubSectionSerializer, JoinRequestSerializer

class AdminClubListCreateView(generics.ListCreateAPIView):
    serializer_class = ClubListSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = Club.objects.all()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs

    def perform_create(self, serializer):
        # 新建社团默认团长为当前 staff
        serializer.save(owner=self.request.user)

class AdminClubDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubListSerializer
    permission_classes = [permissions.IsAdminUser]

# clubs/admin_views.py
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import ClubSection
from .serializers import ClubSectionSerializer

class AdminClubSectionListCreateView(generics.ListCreateAPIView):
    serializer_class = ClubSectionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return ClubSection.objects.filter(club_id=self.kwargs["club_id"]).order_by("order", "id")

    def create(self, request, *args, **kwargs):
        # ✅ 强制把 club 写入数据，避免 {"club": ["This field is required."]}
        data = request.data.copy()
        data["club"] = self.kwargs["club_id"]

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


class AdminSectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClubSection.objects.all()
    serializer_class = ClubSectionSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminJoinRequestListView(generics.ListAPIView):
    serializer_class = JoinRequestSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        club_id = self.kwargs["club_id"]
        return ClubJoinRequest.objects.filter(club_id=club_id, status="pending").order_by("-created_at")
