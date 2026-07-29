from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return Response({'message': 'Welcome to the E-commerce API!'}, status=status.HTTP_200_OK)
