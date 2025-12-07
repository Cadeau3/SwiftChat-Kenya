import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f"chat_{self.room_name}"

        # require authenticated users
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # optional: announce join
        await self.channel_layer.group_send(self.group_name, {
            "type":"chat.system",
            "message": f"{self.scope['user'].username} joined the room."
        })

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_send(self.group_name, {
            "type":"chat.system",
            "message": f"{self.scope['user'].username} left the room."
        })

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        if message:
            # save message to DB
            await self.save_message(self.scope["user"].id, self.room_name, message)
            await self.channel_layer.group_send(self.group_name, {
                "type": "chat.message",
                "username": self.scope["user"].username,
                "message": message
            })
        # typing indicator
        if data.get("typing") is not None:
            await self.channel_layer.group_send(self.group_name, {
                "type": "chat.typing",
                "username": self.scope["user"].username,
                "typing": data["typing"]
            })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type":"message",
            "username": event["username"],
            "message": event["message"]
        }))

    async def chat_system(self, event):
        await self.send(text_data=json.dumps({
            "type":"system",
            "message": event["message"]
        }))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({
            "type":"typing",
            "username": event["username"],
            "typing": event["typing"]
        }))

    @database_sync_to_async
    def save_message(self, user_id, room_name, content):
        user = User.objects.get(id=user_id)
        room, _ = Room.objects.get_or_create(name=room_name)
        return Message.objects.create(room=room, user=user, content=content)
