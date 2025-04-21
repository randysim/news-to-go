from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from modules.job_manager.job_queue import job_queue
from modules.job_manager.jobs import create_video_job, create_script_job, create_scrape_job
from rest_framework.permissions import IsAuthenticated
from ..models import Video

class JobView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, video_id):
        job = job_queue.get_job_by_video_id(video_id)
        if not job:
            return Response({ "job": { "status": "FINISHED" }}, status=status.HTTP_200_OK)
        video = Video.objects.get(id=video_id)

        if video.video_creator != request.user:
            return Response({"error": "You are not authorized to view this job"}, status=status.HTTP_403_FORBIDDEN)

        return Response({"job": {
            "status": job["status"],
            "successful": job["successful"],
            "error": job["error"]
        }}, status=status.HTTP_200_OK)

    def post(self, request, video_id):
        job_type = request.data.get("job_type")

        if not video_id:
            return Response({"error": "Video ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        video = Video.objects.get(id=video_id)
        if video.video_creator != request.user:
            return Response({"error": "You are not authorized to create jobs for this video"}, status=status.HTTP_403_FORBIDDEN)

        job = None
        if job_type == "SCRAPE":
            url = request.data.get("url")
            if not url:
                return Response({"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST)
            job = create_scrape_job(video_id, url)
        elif job_type == "SCRIPT":
            job = create_script_job(video_id)
        elif job_type == "VIDEO":
            job = create_video_job(video_id)
        else:
            return Response({"error": "Invalid job type"}, status=status.HTTP_400_BAD_REQUEST)

        job_queue.enqueue(video_id, job)
        return Response({"message": "Job created"}, status=status.HTTP_200_OK)
