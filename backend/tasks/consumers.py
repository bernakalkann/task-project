import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'tasks_channel_group'
        
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket client
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action', 'task_updated')
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'task_event',
                    'action': action,
                    'task_id': data.get('task_id')
                }
            )
        except Exception:
            pass

    # Receive message from room group broadcast
    async def task_event(self, event):
        # Send message to WebSocket client
        await self.send(text_data=json.dumps({
            'action': event.get('action', 'task_updated'),
            'task_id': event.get('task_id')
        }))
