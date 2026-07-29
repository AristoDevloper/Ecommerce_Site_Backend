from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from EcomApp.models import Conversation, Message, Store
from EcomApp.serializers import ConversationSerializer, MessageSerializer
from EcomApp.customjwtauthentication import CustomJWTAuthentication

class ChatRoomView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        store_id = request.data.get("store_id")
        try:
            store = Store.objects.select_related("owner").get(store_id=store_id)
        except Store.DoesNotExist:
            return Response({'error':'Store does not exist!!!'}, status=status.HTTP_404_NOT_FOUND)
        seller = store.owner
        if not seller:
           return Response({'error':'Seller does not exists!!!'}, status=status.HTTP_404_NOT_FOUND)
        
        conversation = (
            Conversation.objects.filter(user1=seller, user2=request.user).first() or
            Conversation.objects.filter(user1=request.user, user2=seller).first()
        )
        
        created = False
        if not conversation:
            conversation = Conversation.objects.create(user1=seller, user2=request.user)
            created = True

        room_name = str(conversation.uuid).replace('-', '')
        
        if created:
            return Response(
                {
                    "robot_response": f"Thank you for contacting {store.name}. How can we help you?",
                    "conversation_uuid": str(conversation.uuid),
                    "room_name": room_name,
                    "created": True
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                "conversation_uuid": str(conversation.uuid),
                "room_name": room_name,
                "created": False
            }
        )

class ChatMessageView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, room_id):
        try:
            conversation = Conversation.objects.get(uuid=room_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = LimitOffsetPagination()
        paginator.default_limit = 20
        paginator.max_limit = 50
        
        fetched_messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        messages = paginator.paginate_queryset(fetched_messages, request)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    conversations = (
        Conversation.objects.filter(user1=request.user) | 
        Conversation.objects.filter(user2=request.user)
    ).order_by('-created_at').distinct()
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
