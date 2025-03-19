from .generate_script import generate_script, generate_script_file
from .generate_audio import generate_audio_from_script
from .generate_images import generate_keywords, search_media, download_media
from .generate_captions import generate_captions, fix_captions
from .clean import clean_double_space, get_within_tags, clean_characters
import re
import os
from pathlib import Path
import json

from moviepy import *

def get_sentence_starts(script, captions):
    Path(os.getenv("ERROR_DIRECTORY")).mkdir(parents=True, exist_ok=True)

    text = get_within_tags("HOOK", script) + " " + get_within_tags("BODY", script) + " " + get_within_tags("OUTRO", script)
    text = clean_double_space(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    sentence_starts = {}
    current_sentence = 0
    current_word = 0
    current_start = -1
    current_end = -1
    current_sentence_length = len(sentences[current_sentence].split(" "))

    for caption in captions:
        if current_sentence >= len(sentences):
            break

        if current_word == 0:
            current_start = caption[1]

        current_word += 1

        if current_word >= current_sentence_length:
            current_end = caption[2]
            sentence_starts[str(current_sentence)] = {
                "start": current_start,
                "end": current_end,
                "text": sentences[current_sentence]
            }
            
            current_word = 0
            current_sentence += 1
            current_start = -1
            current_end = -1

            if current_sentence < len(sentences):
                current_sentence_length = len(sentences[current_sentence].split(" "))

    if current_sentence < len(sentences):
        sentence_starts[str(current_sentence)] = {
            "start": current_start,
            "end": current_end, # THIS WILL BE -1 WHICH MEANS THE END OF THE VIDEO
            "text": sentences[current_sentence]
        }
    
    return sentence_starts

def gather_video_resources(title, news_content, directory=None):
    if directory:
        Path(directory).mkdir(parents=True, exist_ok=True)

    title = clean_double_space(title)
    title = clean_characters(title)

    filename = title.replace(" ", "_").lower()
    filename = re.sub(r'[^a-z0-9_]', '', filename)

    print(f"Generating script for {title}...")
    summary, script, _, _ = generate_script(news_content)
    Path(os.path.join(directory, "scripts")).mkdir(parents=True, exist_ok=True)
    generate_script_file(filename, os.path.join(directory, "scripts"), summary, script) # Just to track the progress

    print(f"Generating audio for {title}...")
    audio_file_path = generate_audio_from_script(script, filename, os.path.join(directory, "audio"))
    print(f"Audio file saved at {audio_file_path}")
    print(f"Generating captions for {title}...")
    captions = fix_captions(generate_captions(audio_file_path), script)

    print(f"Generating sentence starts for {title}...")
    # to get the end of the first clip, it is the start of the clip index + every_n_sentences and if not then just to the end of the video
    sentence_starts = get_sentence_starts(script, captions)

    every_n_sentences = 2
    print(f"Generating images for {title}...")
    print(f"Generating keywords...")
    keywords = generate_keywords(script, every_n_sentences)
    
    keyword_image_overrides = {}
    for i in range(len(keywords)):
        keyword_image_overrides[str(i)] = { "type": "", "url": ""}

    return title, audio_file_path, keywords, captions, sentence_starts, filename, directory, every_n_sentences, keyword_image_overrides

def create_subtitle_clips(captions, videosize):
    subtitle_clips = []

    for caption in captions:
        word, start_time, end_time = caption
        duration = end_time - start_time

        text_clip = TextClip(font="fonts/Roboto.ttf", text=word, font_size=24, color='white', stroke_color='black', stroke_width=4, size=videosize, method="caption", horizontal_align="center", vertical_align="bottom")
        text_clip = text_clip.with_start(start_time).with_duration(duration)
        subtitle_clips.append(text_clip)

    return subtitle_clips

def construct_video(title, audio_file_path, keywords, captions, sentence_starts, filename, directory, every_n_sentences, keyword_image_overrides):
    urls_used = set()
    medias = []
    current_sentence = 0

    print(f"Downloading media for {title}...")

    for i, kw_data in enumerate(keywords):
        keyword = kw_data["keyword"]

        override = keyword_image_overrides.get(str(i))
        media_url = ""
        media_type = ""
        if override and override.get("url"):
            media_url = override["url"]
            media_type = override["type"]
        else:
            media_url, media_type = search_media(keyword, urls_used)

        urls_used.add(media_url)
        media_path = download_media(media_url, os.path.join(directory, "media", filename))

        medias.append({ "path": media_path, "sentence": current_sentence, "type": media_type })
        print(f"Downloaded {len(medias)}/{len(keywords)} for {title}")

        current_sentence += every_n_sentences
    
    print(f"Editing video for {title}...")
    voice_over = AudioFileClip(audio_file_path)
    total_duration = voice_over.duration # measured in seconds
    
    b_roll = []

    # Create the B-roll
    for media in medias:
        media_path = media["path"]
        sentence_num = media.get("sentence")
        start = sentence_starts[str(sentence_num)]["start"]
        end = sentence_starts[str(sentence_num + every_n_sentences)]["start"] if str(sentence_num + every_n_sentences) in sentence_starts else total_duration
        duration = end - start if end > 0 else total_duration - start

        if media["type"] == "image":
            media_clip = ImageClip(media_path).set_duration(duration)
        else:
            media_clip = VideoFileClip(media_path)
            media_clip.with_volume_scaled(0)
            
            if media_clip.duration > duration:
                media_clip = media_clip.subclipped(0, duration)
            elif media_clip.duration < duration:
                loop_effect = vfx.Loop(duration=duration)
                media_clip = loop_effect.copy().apply(media_clip)

        b_roll.append(media_clip)
    
    video = concatenate_videoclips(b_roll, method="compose")
    video = video.with_audio(voice_over)

    # Create the captions
    subtitle_clips = create_subtitle_clips(captions, video.size)

    final_video = CompositeVideoClip([video] + subtitle_clips)

    # write the video
    Path(os.path.join(directory, "video_output")).mkdir(parents=True, exist_ok=True)
    final_video.write_videofile(os.path.join(directory, "video_output", f"{filename}.mp4"))

def save_config(title, audio_file_path, keywords, captions, sentence_starts, filename, directory, every_n_sentences, keyword_image_overrides, save_dir):
    resources = {
        "title": title,
        "audio_file_path": audio_file_path,
        "keywords": keywords,
        "captions": captions,
        "sentence_starts": sentence_starts,
        "filename": filename,
        "directory": directory,
        "every_n_sentences": every_n_sentences,
        "keyword_image_overrides": keyword_image_overrides
    }

    Path(save_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(save_dir, f"{filename}_config.json")
    with open(file_path, "w") as f:
        f.write(json.dumps(resources))
    
    return file_path

def load_config(path):
    with open(path, "r") as f:
        resources = json.load(f)
    
    return resources["title"], resources["audio_file_path"], resources["keywords"], resources["captions"], resources["sentence_starts"], resources["filename"], resources["directory"], resources["every_n_sentences"], resources["keyword_image_overrides"]