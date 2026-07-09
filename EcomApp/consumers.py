from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, Conversation
from channels.generic.websocket import WebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_name}'

        if not self.scope.get('user') or isinstance(self.scope['user'], AnonymousUser) or not self.scope['user'].is_authenticated:
            self.close()
            return

        # Join room group 
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )    

    def receive(self, text_data):
        if not self.scope.get('user') or isinstance(self.scope['user'], AnonymousUser) or not self.scope['user'].is_authenticated:
            self.close()
            return

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save the message to the database
        user = self.scope['user']
        self.save_message(user, message)

        # sending mmesage to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


    def save_message(self, user, message):
        # Save the message to the database
        conversation, created = Conversation.objects.get_or_create(uuid=self.room_id)
        Message.objects.create(conversation=conversation, sender=user, content=message)