from rest_framework import serializers
from .models import ChatGroup, GroupMember, GroupMessage


class ChatGroupSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source="creator.username", read_only=True)
    members_count = serializers.IntegerField(source="members.count", read_only=True)
    is_member = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = ChatGroup
        fields = [
            "id",
            "name",
            "description",
            "creator",
            "creator_username",
            "is_public",
            "members_count",
            "is_member",
            "my_role",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "creator",
            "creator_username",
            "members_count",
            "is_member",
            "my_role",
            "created_at",
        ]

    def _membership(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        return GroupMember.objects.filter(group=obj, user=user).first()

    def get_is_member(self, obj):
        return self._membership(obj) is not None

    def get_my_role(self, obj):
        membership = self._membership(obj)
        return membership.role if membership else ""


class GroupMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = GroupMessage
        fields = ["id", "group", "sender", "sender_username", "msg_type", "content", "created_at"]
        read_only_fields = ["id", "sender", "sender_username", "created_at"]
