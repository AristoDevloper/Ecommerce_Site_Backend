from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, Conversation
from channels.generic.websocket import WebsocketConsumer
import json
from django.shortcuts import get_object_or_404

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

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
        pass

    def broadcast_message(self,event):
        pass

    def save_message(self, user, message):
        # Save the message to the database
        conversation, created = Conversation.objects.get_or_create(room_name=self.room_name)
        Message.objects.create(conversation=conversation, user=user, content=message)