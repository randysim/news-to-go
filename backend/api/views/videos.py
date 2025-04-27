from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import VideoSerializer
from ..models import Video
from rest_framework import status
import json
import os
from django.http import FileResponse
from django.conf import settings

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
    
    def patch(self, request, id):
        video = Video.objects.get(id=id)
        
        # Check if user has permission to update the video
        if video.video_creator != request.user:
            return Response({"detail": "You do not have permission to update this video."}, status=status.HTTP_403_FORBIDDEN)
        
        # Get valid fields from the model, excluding system-managed fields
        system_fields = ['id', 'created_at', 'updated_at']
        valid_fields = [f.name for f in Video._meta.get_fields() if not f.is_relation and f.name not in system_fields]
        
        # Check if request contains any invalid fields
        invalid_fields = [field for field in request.data.keys() if field not in valid_fields]
        if invalid_fields:
            return Response(
                {"detail": f"Invalid fields: {', '.join(invalid_fields)}. Valid fields are: {', '.join(valid_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate config
        if "config" in request.data:
            config = json.loads(request.data["config"])
            old_config = json.loads(video.config)

            # compare lengths, cannot change length of new config
            if len(config["keywords"]) != len(old_config["keywords"]):
                return Response({"detail": "Cannot change length of config keywords"}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(config["keyword_image_overrides"]) != len(old_config["keyword_image_overrides"]):
                return Response({"detail": "Cannot change length of config keyword_image_overrides"}, status=status.HTTP_400_BAD_REQUEST)
            
            # check if each keyword has the proper fields and lengths
            for i in range(len(config["keywords"])):
                if len(config["keywords"][i]["keyword"]) != 2:
                    return Response({"detail": "Keyword must have 2 values"}, status=status.HTTP_400_BAD_REQUEST)
                if "fragment" not in config["keywords"][i]:
                    return Response({"detail": "Keyword must have a fragment field"}, status=status.HTTP_400_BAD_REQUEST)
                if "keyword" not in config["keywords"][i]:
                    return Response({"detail": "Keyword must have a keyword field"}, status=status.HTTP_400_BAD_REQUEST)
                if "idx" not in config["keywords"][i]:
                    return Response({"detail": "Keyword must have a idx field"}, status=status.HTTP_400_BAD_REQUEST)
                
                if int(config["keywords"][i]["idx"]) != i:
                    return Response({"detail": "Keyword idx must be the same as the index"}, status=status.HTTP_400_BAD_REQUEST)
                if type(config["keywords"][i]["fragment"]) != str:
                    return Response({"detail": "Keyword fragment must be a string"}, status=status.HTTP_400_BAD_REQUEST)
                if len(config["keywords"][i]["keyword"]) != 2:
                    return Response({"detail": "Keyword must have 2 values"}, status=status.HTTP_400_BAD_REQUEST)
                if type(config["keywords"][i]["keyword"][0]) != str or type(config["keywords"][i]["keyword"][1]) != str:
                    return Response({"detail": "Keyword must be a list of strings"}, status=status.HTTP_400_BAD_REQUEST)
                
            # check if each keyword_image_override has the proper fields and lengths
            for value in config["keyword_image_overrides"].values():
                if "url" not in value:
                    return Response({"detail": "Keyword image override must have a url field"}, status=status.HTTP_400_BAD_REQUEST)
                if "type" not in value:
                    return Response({"detail": "Keyword image override must have a type field"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Only update fields that are included in the request
        serializer = VideoSerializer(video, data=request.data, partial=True)
        
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

class VideoFileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        try:
            video = Video.objects.get(id=id)
            
            # Check if user has permission to access the video
            if video.video_creator != request.user:
                return Response({"detail": "You do not have permission to access this video."}, status=status.HTTP_403_FORBIDDEN)
            
            # Construct the video file path
            video_path = os.path.join(settings.BASE_DIR, 'resource', 'video_output', f'{id}.mp4')
            
            # Check if the file exists
            if not os.path.exists(video_path):
                return Response({"detail": "Video file not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Serve the video file
            response = FileResponse(open(video_path, 'rb'))
            response['Content-Type'] = 'video/mp4'
            response['Content-Disposition'] = f'inline; filename="{id}.mp4"'
            return response
            
        except Video.DoesNotExist:
            return Response({"detail": "Video not found."}, status=status.HTTP_404_NOT_FOUND)
        
        