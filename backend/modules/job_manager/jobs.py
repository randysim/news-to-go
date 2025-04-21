from api.models import Video
from ..scraper.scrape_generic import scrape_generic
from ..video.generate_script import generate_script
from ..video.generate_images import generate_keywords
from ..video.generate_video import construct_video, get_sentence_starts
from ..video.generate_audio import generate_audio_from_script
from ..video.generate_captions import generate_captions, fix_captions
from ..utils import debug_print
import json

def create_scrape_job(video_id: int, url: str):
    def job():
        video = Video.objects.get(id=video_id)

        title, content = scrape_generic(url)
        video.news_url = url
        video.news_title = title
        video.news_content = content

        debug_print(f"Scraped {url} for video {video_id}")

        video.save()
    return job

def create_script_job(video_id: int):
    def job():
        video = Video.objects.get(id=video_id)

        news_title = video.news_title
        news_content = video.news_content

        debug_print(f"Generating script for {news_title}...")

        _, script, _, _ = generate_script(news_content)

        keywords = generate_keywords(script, every_n_sentences=1, empty=True)
        keyword_image_overrides = {
            str(i): {
                "type": "",
                "url": ""
            }
            for i in range(len(keywords))
        }

        config = {
            "keywords": keywords,
            "keyword_image_overrides": keyword_image_overrides
        }

        video.script = script
        video.config = json.dumps(config)
        video.save()

        debug_print(f"Script generated for {news_title}")
    return job

def create_video_job(video_id: int):
    def job():
        video = Video.objects.get(id=video_id)

        config = json.loads(video.config)
        keywords = config["keywords"]
        keyword_image_overrides = config["keyword_image_overrides"]

        debug_print(f"Generating video for {video.news_title}...")

        audio_file_path = generate_audio_from_script(video.script, video.news_title, video.directory)

        captions = fix_captions(generate_captions(audio_file_path), video.script)

        sentence_starts = get_sentence_starts(video.script, captions)

        construct_video(
            title=video.news_title,
            audio_file_path=audio_file_path,
            keywords=keywords,
            captions=captions,
            sentence_starts=sentence_starts,
            filename=str(video.id),
            directory="resource",
            every_n_sentences=1,
            keyword_image_overrides=keyword_image_overrides
        )

        debug_print(f"Video generated for {video.news_title}")

    return job





