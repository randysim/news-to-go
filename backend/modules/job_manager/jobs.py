def create_script_job(video_id: int):
    def job():
        video = Video.objects.get(id=video_id)
        video.script = create_script(video)
        video.save()
    return job

