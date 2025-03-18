from ..scraper.scrape_generic import scrape_generic
from .generate_script import generate_script
from .generate_audio import generate_audio_from_script
from .generate_images import generate_keywords, search_media, download_media
from .generate_captions import generate_captions, fix_captions
from .clean import clean_double_space, get_within_tags
import re
import os
from pathlib import Path

def get_sentence_starts(script, captions):
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

def generate_video(news_url, directory=None):
    if directory:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print(f"Scraping {news_url}...")
    title, content = scrape_generic(news_url)
    title = clean_double_space(title)

    filename = title.replace(" ", "_").lower()
    filename = re.sub(r'[^a-z0-9_]', '', filename)

    print(f"Generating script for {title}...")
    script = generate_script(content)

    print(f"Generating audio for {title}...")
    audio_file_path = generate_audio_from_script(script, filename, os.path.join(directory, "audio"))
    print(f"Audio file saved at {audio_file_path}")
    print(f"Generating captions for {title}...")
    captions = fix_captions(generate_captions(audio_file_path), script)

    print(f"Generating sentence starts for {title}...")
    sentence_starts = get_sentence_starts(script, captions)

    every_n_sentences = 2
    print(f"Generating images for {title}...")
    keywords = generate_keywords(script, every_n_sentences)
    used_keywords = {}
    media = []
    current_sentence = 0

    print(f"Downloading media for {title}...")

    for keyword in keywords:
        nth = max(used_keywords.get(keyword[0], 0), used_keywords.get(keyword[1], 0))
        used_keywords[keyword[0]] += 1
        used_keywords[keyword[1]] += 1

        media = search_media(keyword, nth)
        media_path = download_media(media, os.path.join(directory, "media", filename))

        media.append({ "path": media_path, "sentence": current_sentence })
        print(f"Downloaded {len(media)}/{len(keywords)} for {title}")

        current_sentence += every_n_sentences
    
    """
    HAVE:
    - path to audio file
    - path to media files (and for what sentence they begin) <- could be image or video
    - captions and their start and end times
    - sentence starts and their start and end times 
    """
    
    
    

        


