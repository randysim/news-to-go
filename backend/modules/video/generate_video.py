from .generate_script import generate_script, generate_script_file
from .generate_audio import generate_audio_from_script
from .generate_images import generate_keywords, search_media, download_media
from .generate_captions import generate_captions, fix_captions
from .clean import clean_double_space, get_within_tags, clean_characters
import re
import os
from pathlib import Path

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
            sentence_starts[current_sentence] = {
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
    if current_word > 0:
        sentence_starts[current_sentence] = {
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
    used_keywords = {}
    medias = []
    current_sentence = 0

    print(f"Keywords: {keywords}")

    print(f"Downloading media for {title}...")

    for keyword in keywords:
        nth = max(used_keywords.get(keyword[0], 0), used_keywords.get(keyword[1], 0))
        used_keywords[keyword[0]] = used_keywords.get(keyword[0], 0) + 1
        used_keywords[keyword[1]] = used_keywords.get(keyword[1], 0) + 1

        media_url, media_type = search_media(keyword, nth)
        media_path = download_media(media_url, os.path.join(directory, "media", filename))

        medias.append({ "path": media_path, "sentence": current_sentence, "type": media_type })
        print(f"Downloaded {len(medias)}/{len(keywords)} for {title}")

        current_sentence += every_n_sentences
    
    """
    HAVE:
    - path to audio file (audio_file_path)
    - path to media files (media) (and for what sentence they begin) <- could be image or video
    - captions and their start and end times (captions)
    - sentence starts and their start and end times (sentence_starts)
    """

    return audio_file_path, medias, captions, sentence_starts, filename, directory, every_n_sentences

def construct_video(audio_file_path, medias, captions, sentence_starts, filename, directory, every_n_sentences):
    print(f"Editing video for...")
    voice_over = AudioFileClip(audio_file_path)
    total_duration = voice_over.duration # measured in seconds
    
    b_roll = []

    # Create the B-roll
    for media in medias:
        media_path = media["path"]
        sentence_num = media.get("sentence")
        start = sentence_starts[sentence_num]["start"]
        end = sentence_starts[sentence_num + every_n_sentences]["start"] if sentence_num + every_n_sentences in sentence_starts else total_duration
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

    # write the video
    Path(os.path.join(directory, "video_output")).mkdir(parents=True, exist_ok=True)
    video.write_videofile(os.path.join(directory, "video_output", f"{filename}.mp4"))