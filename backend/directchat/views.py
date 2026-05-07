from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from .models import DirectThread, DirectMessage
from .serializers import DirectThreadSerializer, DirectMessageSerializer


class ThreadListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DirectThreadSerializer

    def get_queryset(self):
        u = self.request.user
        return (
            DirectThread.objects.filter(Q(user1=u) | Q(user2=u))
            .select_related("user1", "user2")
            .prefetch_related("messages__sender")
        )


class ThreadCreateView(APIView):
    """
    POST /api/dm/threads/
    body: { "to_username": "test002" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        to_username = (request.data.get("to_username") or "").strip()
        if not to_username:
            return Response({"to_username": ["对方用户名不能为空"]}, status=status.HTTP_400_BAD_REQUEST)

        if to_username == request.user.username:
            return Response({"to_username": ["不能和自己私聊"]}, status=status.HTTP_400_BAD_REQUEST)

        other = User.objects.filter(username=to_username).first()
        if not other:
            return Response({"to_username": ["用户不存在"]}, status=status.HTTP_404_NOT_FOUND)

        a, b = DirectThread.normalize_pair(request.user.id, other.id)
        thread, _ = DirectThread.objects.get_or_create(user1_id=a, user2_id=b)

        data = DirectThreadSerializer(thread, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)


class MessageListView(generics.ListAPIView):
    """
    GET /api/dm/threads/<thread_id>/messages/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DirectMessageSerializer

    def get_queryset(self):
        thread_id = self.kwargs["thread_id"]
        u = self.request.user
        # 必须是会话成员
        ok = DirectThread.objects.filter(id=thread_id).filter(Q(user1=u) | Q(user2=u)).exists()
        if not ok:
            return DirectMessage.objects.none()
        return DirectMessage.objects.filter(thread_id=thread_id).select_related("sender")
