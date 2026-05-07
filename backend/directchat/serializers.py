from rest_framework import serializers
from .models import DirectThread, DirectMessage


class DirectThreadSerializer(serializers.ModelSerializer):
    other_user_id = serializers.SerializerMethodField()
    other_username = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = DirectThread
        fields = ["id", "user1", "user2", "created_at", "other_user_id", "other_username", "last_message"]
        read_only_fields = fields

    def _get_other_user(self, obj: DirectThread):
        req = self.context.get("request")
        if not req or not req.user.is_authenticated:
            return None
        if obj.user1_id == req.user.id:
            return obj.user2
        return obj.user1

    def get_other_user_id(self, obj):
        u = self._get_other_user(obj)
        return u.id if u else None

    def get_other_username(self, obj):
        u = self._get_other_user(obj)
        return u.username if u else None

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        if not last:
            return None
        return {
            "id": last.id,
            "sender_username": last.sender.username,
            "content": last.content,
            "created_at": last.created_at.isoformat(),
        }


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = DirectMessage
        fields = ["id", "thread", "sender", "sender_username", "content", "created_at"]
        read_only_fields = ["id", "sender", "sender_username", "created_at"]
