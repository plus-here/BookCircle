from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatGroup, GroupMember, GroupMessage
from .serializers import ChatGroupSerializer, GroupMessageSerializer


class GroupListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatGroupSerializer

    def get_queryset(self):
        # 你创建的 + 你加入的 + 公开群（演示版）
        my_group_ids = GroupMember.objects.filter(user=self.request.user).values_list("group_id", flat=True)
        return (
            ChatGroup.objects.filter(is_public=True)
            | ChatGroup.objects.filter(id__in=my_group_ids)
            | ChatGroup.objects.filter(creator=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        group = serializer.save(creator=self.request.user)
        GroupMember.objects.get_or_create(group=group, user=self.request.user, defaults={"role": "owner"})


class GroupJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = ChatGroup.objects.filter(id=group_id).first()
        if not group:
            return Response({"detail": "群组不存在"}, status=status.HTTP_404_NOT_FOUND)
        GroupMember.objects.get_or_create(group=group, user=request.user, defaults={"role": "member"})
        return Response({"detail": "已加入群组"}, status=status.HTTP_200_OK)


class GroupLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        deleted, _ = GroupMember.objects.filter(group_id=group_id, user=request.user).delete()
        if deleted == 0:
            return Response({"detail": "你不在该群组中"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "已退出群组"}, status=status.HTTP_200_OK)


class GroupMessageListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupMessageSerializer

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        # 必须是成员才能看历史消息
        if not GroupMember.objects.filter(group_id=group_id, user=self.request.user).exists():
            return GroupMessage.objects.none()
        return GroupMessage.objects.filter(group_id=group_id).select_related("sender")
