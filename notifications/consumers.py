from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs'].get('user_id')
        self.group_name = f"user_{self.user_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"[WS] {self.user_id} connected and joined group {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"[WS] {self.user_id} disconnected from group {self.group_name}")

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({"echo": text_data}))

    async def send_notification(self, event):
        logger.info(f"[WS] send_notification called with event: {event}")
        await self.send(text_data=json.dumps(event['content']))
