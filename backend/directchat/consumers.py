import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Q

from accounts.models import User
from .models import DirectThread, DirectMessage


class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = int(self.scope["url_route"]["kwargs"]["thread_id"])
        self.room_group_name = f"dm_{self.thread_id}"

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

        ok = await self.is_thread_member(self.thread_id, self.user.id)
        if not ok:
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

        # ---- WebRTC 信令：转发给会话内另一端 ----
        signal = data.get("signal")
        if signal:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "dm_signal",
                    "signal": signal,
                    "from": self.user.username,
                },
            )
            return

        # ---- 普通文字消息 ----
        msg = (data.get("message") or "").strip()
        if not msg:
            return

        obj = await self.save_message(self.thread_id, self.user.id, msg)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "dm_message",
                "id": obj["id"],
                "sender_username": obj["sender_username"],
                "message": obj["content"],
                "created_at": obj["created_at"],
            },
        )

    async def dm_message(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    async def dm_signal(self, event):
        # ✅ 不回显给发送者，避免自己收到自己的 offer/ice/answer/hangup
        if event.get("from") == self.user.username:
            return
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
    def is_thread_member(self, thread_id, user_id):
        return DirectThread.objects.filter(id=thread_id).filter(
            Q(user1_id=user_id) | Q(user2_id=user_id)
        ).exists()

    @sync_to_async
    def save_message(self, thread_id, user_id, content):
        obj = DirectMessage.objects.create(thread_id=thread_id, sender_id=user_id, content=content)
        return {
            "id": obj.id,
            "sender_username": obj.sender.username,
            "content": obj.content,
            "created_at": obj.created_at.isoformat(),
        }
