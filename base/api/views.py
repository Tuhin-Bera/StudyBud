from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


@api_view(['GET'])
def get_routes(request):
    route = [
        'GET /api',
        'GET /api/room',
        'GET /api/room/id'
    ]
    return Response(route)

@api_view(['GET'])
def get_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_room(request, pk):
    room = Room.objects.get(id = pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)