from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Message, Conversation
import json
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        user = self.scope.get('user')

        # Reject unauthenticated users
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            self.close(code=4001)
            return

        # Check if conversation exists and user is a participant
        try:
            conversation = Conversation.objects.get(uuid=self.room_id)
        except Conversation.DoesNotExist:
            self.close(code=4004)
            return

        if conversation.user1 != user and conversation.user2 != user:
            self.close(code=4003)
            return

        self.conversation = conversation

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )

    def receive(self, text_data):
        user = self.scope.get('user')

        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            self.close(code=4001)
            return

        # Check if conversation exists and user is a participant
        try:
            conversation = Conversation.objects.get(uuid=self.room_id)
        except Conversation.DoesNotExist:
            self.close(code=4004)
            return

        if conversation.user1 != user and conversation.user2 != user:
            self.close(code=4003)
            return

        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_content = text_data_json.get('message', '').strip()

        if not message_content:
            return

        # Save the message to the database
        saved_message = Message.objects.create(
            conversation=self.conversation,
            sender=user,
            content=message_content
        )

        # Broadcast to room group with sender info and timestamp
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': user.id,
                'sender_username': user.username,
                'message_id': saved_message.id,
                'created_at': saved_message.created_at.isoformat(),
            }
        )

    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'message_id': event['message_id'],
            'created_at': event['created_at'],
        }))