# clubs/views.py
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Club, ClubSection, ClubJoinRequest, ClubMembership, Post, Comment
from .serializers import (
    ClubListSerializer,
    ClubSectionSerializer,
    JoinRequestSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    MembershipSerializer,
    PostCreateSerializer,
    CommentCreateSerializer,
)

from .permissions import IsClubAdmin


class ClubListView(generics.ListAPIView):
    serializer_class = ClubListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Club.objects.all()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs


class ClubDetailView(generics.RetrieveAPIView):
    queryset = Club.objects.all()
    serializer_class = ClubListSerializer
    permission_classes = [permissions.AllowAny]


class ClubSectionListView(generics.ListAPIView):
    serializer_class = ClubSectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        club_id = self.kwargs["club_id"]
        return ClubSection.objects.filter(club_id=club_id).order_by("order", "id")


class ClubMemberListView(generics.ListAPIView):
    """
    GET /api/clubs/<club_id>/members/
    """
    serializer_class = MembershipSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        club_id = self.kwargs["club_id"]
        return ClubMembership.objects.filter(club_id=club_id).select_related("user").order_by("role", "-joined_at")


class ClubMeView(APIView):
    """
    GET /api/clubs/<club_id>/me/
    返回当前登录用户在该社团的状态：是否成员/角色/申请状态
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, club_id):
        membership = ClubMembership.objects.filter(club_id=club_id, user=request.user).first()
        jr = ClubJoinRequest.objects.filter(club_id=club_id, user=request.user).first()

        return Response(
            {
                "is_member": bool(membership),
                "role": membership.role if membership else None,
                "join_request_status": jr.status if jr else None,
                "join_request_id": jr.id if jr else None,
            },
            status=status.HTTP_200_OK,
        )


class JoinClubView(APIView):
    """
    POST /api/clubs/<club_id>/join/
    body: { "reason": "..." }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, club_id):
        club = Club.objects.filter(id=club_id).first()
        if not club:
            return Response({"detail": "社团不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 已是成员
        if ClubMembership.objects.filter(club_id=club_id, user=request.user).exists():
            return Response({"detail": "你已加入该社团"}, status=status.HTTP_400_BAD_REQUEST)

        # 已申请过
        obj, created = ClubJoinRequest.objects.get_or_create(club_id=club_id, user=request.user)
        if not created and obj.status == "pending":
            return Response({"detail": "已提交申请，请等待审批"}, status=status.HTTP_400_BAD_REQUEST)

        obj.status = "pending"
        obj.reason = request.data.get("reason", "")
        obj.reviewed_at = None
        obj.reviewed_by = None
        obj.save()
        return Response(JoinRequestSerializer(obj).data, status=status.HTTP_201_CREATED)


class JoinRequestListView(generics.ListAPIView):
    """
    GET /api/clubs/<club_id>/requests/   社团管理员查看待审批申请
    """
    serializer_class = JoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsClubAdmin]

    def get_queryset(self):
        club_id = self.kwargs["club_id"]
        return ClubJoinRequest.objects.filter(club_id=club_id, status="pending").order_by("-created_at")


class ApproveJoinRequestView(APIView):
    """
    POST /api/requests/<request_id>/approve/
    POST /api/requests/<request_id>/reject/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id, action):
        jr = ClubJoinRequest.objects.filter(id=request_id).select_related("club").first()
        if not jr:
            return Response({"detail": "申请不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 权限：社团 owner/admin
        is_admin = request.user.is_staff or ClubMembership.objects.filter(
            club=jr.club, user=request.user, role__in=["owner", "admin"]
        ).exists()
        if not is_admin:
            return Response({"detail": "无权限"}, status=status.HTTP_403_FORBIDDEN)

        if jr.status != "pending":
            return Response({"detail": "该申请已处理"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "approve":
            jr.status = "approved"
            ClubMembership.objects.get_or_create(club=jr.club, user=jr.user, defaults={"role": "member"})
        elif action == "reject":
            jr.status = "rejected"
        else:
            return Response({"detail": "非法操作"}, status=status.HTTP_400_BAD_REQUEST)

        jr.reviewed_at = timezone.now()
        jr.reviewed_by = request.user
        jr.save()
        return Response(JoinRequestSerializer(jr).data, status=status.HTTP_200_OK)


class SectionPostListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/sections/<section_id>/posts/
    POST /api/sections/<section_id>/posts/  {title, content}
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        section_id = self.kwargs["section_id"]
        return Post.objects.filter(section_id=section_id).select_related("author", "section", "club")

    def get_serializer_class(self):
        return PostListSerializer if self.request.method == "GET" else PostDetailSerializer

    def create(self, request, *args, **kwargs):
        section_id = self.kwargs["section_id"]
        section = ClubSection.objects.filter(id=section_id).select_related("club").first()
        if not section:
            return Response({"detail": "板块不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 必须是社团成员才能发帖
        if not ClubMembership.objects.filter(club=section.club, user=request.user).exists():
            return Response({"detail": "加入社团后才能发帖"}, status=status.HTTP_403_FORBIDDEN)

        post = Post.objects.create(
            club=section.club,
            section=section,
            author=request.user,
            title=request.data.get("title", ""),
            content=request.data.get("content", ""),
        )
        return Response(PostDetailSerializer(post).data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all().select_related("author", "section", "club")
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/posts/<post_id>/comments/
    POST /api/posts/<post_id>/comments/  {content}
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id).select_related("author")

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs["post_id"]
        post = Post.objects.filter(id=post_id).select_related("club").first()
        if not post:
            return Response({"detail": "帖子不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 必须是社团成员才能评论
        if not ClubMembership.objects.filter(club=post.club, user=request.user).exists():
            return Response({"detail": "加入社团后才能评论"}, status=status.HTTP_403_FORBIDDEN)

        c = Comment.objects.create(post=post, author=request.user, content=request.data.get("content", ""))
        return Response(CommentSerializer(c).data, status=status.HTTP_201_CREATED)
