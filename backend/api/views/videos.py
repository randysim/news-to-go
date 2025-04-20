from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import VideoSerializer
from ..models import Video
from rest_framework import status

class VideoView(APIView):
    permission_classes = [IsAuthenticated]

    # get all user videos
    def get(self, request):
        videos = Video.objects.filter(video_creator=request.user)
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(video_creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VideoDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        video = Video.objects.get(id=id)

        if video.video_creator != request.user:
            return Response({"detail": "You do not have permission to access this video."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = VideoSerializer(video)
        return Response(serializer.data)
    
    def put(self, request, id):
        video = Video.objects.get(id=id)
        serializer = VideoSerializer(video, data=request.data)

        if video.video_creator != request.user:
            return Response({"detail": "You do not have permission to update this video."}, status=status.HTTP_403_FORBIDDEN)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        video = Video.objects.get(id=id)

        if video.video_creator != request.user:
            return Response({"detail": "You do not have permission to delete this video."}, status=status.HTTP_403_FORBIDDEN)
        
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        