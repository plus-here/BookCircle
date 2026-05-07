import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User
from .models import GroupMember, GroupMessage


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = int(self.scope["url_route"]["kwargs"]["group_id"])
        self.room_group_name = f"group_{self.group_id}"

        # 从 ?token=xxx 取 token
        query = parse_qs(self.scope["query_string"].decode())
        token = (query.get("token") or [None])[0]
        if not token:
            await self.close()
            return

        user = await self.get_user_from_token(token)
        if not user:
            await self.close()
            return

        self.user = user

        # 必须是群成员才能连接聊天室
        is_member = await self.is_member(self.group_id, self.user.id)
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except:
            return

        msg = (data.get("message") or "").strip()
        if not msg:
            return

        # 保存消息
        msg_obj = await self.save_message(self.group_id, self.user.id, msg)

        # 广播给房间
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": msg_obj["id"],
                "sender_username": msg_obj["sender_username"],
                "message": msg_obj["content"],
                "created_at": msg_obj["created_at"],
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    @sync_to_async
    def get_user_from_token(self, token):
        try:
            access = AccessToken(token)
            user_id = access["user_id"]
            return User.objects.filter(id=user_id).first()
        except:
            return None

    @sync_to_async
    def is_member(self, group_id, user_id):
        return GroupMember.objects.filter(group_id=group_id, user_id=user_id).exists()

    @sync_to_async
    def save_message(self, group_id, user_id, content):
        obj = GroupMessage.objects.create(group_id=group_id, sender_id=user_id, msg_type="text", content=content)
        return {
            "id": obj.id,
            "sender_username": obj.sender.username,
            "content": obj.content,
            "created_at": obj.created_at.isoformat(),
        }
