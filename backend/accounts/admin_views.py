from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import User
from .admin_serializers import UserAdminSerializer


class AdminUserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserAdminSerializer

    def get_queryset(self):
        qs = User.objects.all().order_by("-created_at")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(username__icontains=q)
        return qs


class AdminUserRUDView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserAdminSerializer
    queryset = User.objects.all()

    def perform_update(self, serializer):
        # 非 superuser 只能改 is_active / email（不让乱改角色）
        if not self.request.user.is_superuser:
            if "is_staff" in serializer.validated_data:
                raise PermissionDenied("Only superuser can change is_staff")
        serializer.save()
