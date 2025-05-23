import re
import os
import requests
from urllib.parse import urlparse
from pathlib import Path
from ollama import Client
from .clean import get_within_tags, clean_think, clean_double_newlines, clean_double_space, clean_main_quotes, clean_non_ascii, clean_colons, clean_html_tags
from datetime import datetime
from ..utils import debug_print

KEYWORD_MESSAGE = """You are a specialized keyword generator for image searches. When given text, generate ONE highly specific two-word keyword phrase that precisely captures the unique technical context of the provided content.

Avoid generic terms like "action words" or broad category nouns. Instead, focus on technical terminology, specific concepts, or distinctive elements from the text.

Your keyword should be:
- Exactly two words
- Highly specific to the technical subject matter
- Useful for finding relevant technical images
- Be tangible and concrete, not abstract ideas or actions

Format your response exactly as follows: <KEYWORD>{your two-word keyword}</KEYWORD>
"""

def generate_fragments(script, image_every=2):
    text = get_within_tags("HOOK", script) + " " + get_within_tags("BODY", script) + " " + get_within_tags("OUTRO", script)
    text = clean_double_space(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    fragments = []
    total_fragments = (len(sentences) + image_every - 1)//image_every

    for i in range(total_fragments):
        fragment = ". ".join(sentences[i*image_every:i*image_every+image_every])
        fragments.append(fragment)
    
    return fragments

def clean_keyword(text):
    cleaned_keyword = clean_think(text)
    cleaned_keyword = get_within_tags("KEYWORD", cleaned_keyword)
    cleaned_keyword.replace(",", " ")
    cleaned_keyword.replace(";", " ")
    cleaned_keyword = clean_html_tags(cleaned_keyword)
    cleaned_keyword = clean_double_newlines(cleaned_keyword)
    cleaned_keyword = clean_double_space(cleaned_keyword)
    cleaned_keyword = clean_non_ascii(cleaned_keyword)
    cleaned_keyword = clean_colons(cleaned_keyword)
    cleaned_keyword = clean_main_quotes(cleaned_keyword)
    
    return cleaned_keyword

def is_valid_keyword(text):
    if "<KEYWORD>" in text and "</KEYWORD>" in text:
        kw = clean_keyword(text)
        return len(kw.split(" ")) >= 2
    return False

def generate_keyword(text):
    client = Client(
        host=f"http://{os.getenv('OLLAMA_IP')}:11434"
    )

    MODEL = os.getenv("OLLAMA_MODEL")

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": KEYWORD_MESSAGE
            },
            {
                "role": "user",
                "content": f"Generate a word or phrase that best describes the following text:\n{text}"
            }
        ]
    )

    while not is_valid_keyword(response["message"]["content"]):
        debug_print("Invalid keyword. Trying again...")

        now = datetime.now()
        formatted_date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        error_file = os.path.join(os.getenv("ERROR_DIRECTORY"), f"KEYWORD_ERROR_{formatted_date_str}.txt")
        with open(error_file, "w") as f:
            f.write(response["message"]["content"])

        response = client.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": KEYWORD_MESSAGE
                },
                {
                    "role": "user",
                    "content": f"Generate a word or phrase that best describes the following text:\n{text}"
                }
            ]
        )

    keyword = clean_keyword(response["message"]["content"]).split(" ")

    return [keyword[0].lower(), keyword[1].lower()]

def generate_keywords(script, every_n_sentences=2, empty=False):
    fragments = generate_fragments(script, image_every=every_n_sentences)

    keywords = []
    cur = 0
    for fragment in fragments:
        keyword = ""
        if not empty:
            keyword = generate_keyword(fragment)
        else:
            keyword = ["", ""]

        keywords.append({
            "fragment": fragment,
            "keyword": keyword,
            "idx": str(cur)
        })
        cur += 1
        debug_print(f"Generated keyword: {' '.join(keywords[-1].get('keyword'))} -- {cur}/{len(fragments)}")
    
    return keywords

def search_media(keyword, urls_used):
    # Base URLs for Pexels API
    VIDEO_SEARCH_URL = 'https://api.pexels.com/videos/search'
    IMAGE_SEARCH_URL = 'https://api.pexels.com/v1/search'

    # Combine keywords for the search
    combined_keywords = (' '.join(keyword)).strip().lower()

    # Headers for the API request
    headers = {
        'Authorization': os.getenv("PEXELS_API_KEY")
    }

    # Step 1: Search for a video with combined keywords
    response = requests.get(VIDEO_SEARCH_URL, headers=headers, params={'query': combined_keywords, 'per_page': 12})
    if response.status_code == 200:
        data = response.json()
        if data.get('videos'):
            # Check each video until we find one not in urls_used
            for video in data['videos']:
                video_files = video['video_files']
                if video_files:
                    # Filter for files with height <= 1080
                    hd_files = [f for f in video_files if f.get('height', 0) <= 1080]
                    if hd_files:
                        # Sort by height (resolution) in descending order and get the highest one under 1080p
                        hd_files.sort(key=lambda x: x.get('height', 0), reverse=True)
                        video_url = hd_files[0]['link']
                        if video_url not in urls_used:
                            urls_used.add(video_url)
                            return video_url, "video"

    # Step 2: Search for a video with the first keyword only
    response = requests.get(VIDEO_SEARCH_URL, headers=headers, params={'query': keyword[0], 'per_page': 12})
    if response.status_code == 200:
        data = response.json()
        if data.get('videos'):
            for video in data['videos']:
                video_files = video['video_files']
                if video_files:
                    # Filter for files with height <= 1080
                    hd_files = [f for f in video_files if f.get('height', 0) <= 1080]
                    if hd_files:
                        # Sort by height (resolution) in descending order
                        hd_files.sort(key=lambda x: x.get('height', 0), reverse=True)
                        video_url = hd_files[0]['link']
                        if video_url not in urls_used:
                            urls_used.add(video_url)
                            return video_url, "video"

    # Step 3: Search for an image with combined keywords
    response = requests.get(IMAGE_SEARCH_URL, headers=headers, params={'query': combined_keywords, 'per_page': 10})
    if response.status_code == 200:
        data = response.json()
        if data.get('photos'):
            for photo in data['photos']:
                image_url = photo['src']['original']
                if image_url not in urls_used:
                    urls_used.add(image_url)
                    return image_url, "image"

    # Step 4: Search for an image with the first keyword only
    response = requests.get(IMAGE_SEARCH_URL, headers=headers, params={'query': keyword[0], 'per_page': 10})
    if response.status_code == 200:
        data = response.json()
        if data.get('photos'):
            for photo in data['photos']:
                image_url = photo['src']['original']
                if image_url not in urls_used:
                    urls_used.add(image_url)
                    return image_url, "image"

    # Step 5: Return a default image if all searches fail
    default_url = 'https://images.pexels.com/photos/281260/pexels-photo-281260.jpeg'
    if default_url not in urls_used:
        urls_used.add(default_url)
    return default_url, "image"



def download_media(url, directory=None):
    # Create the directory if it doesn't exist
    if directory:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # If filename is empty or doesn't have an extension, create a default one
        if not filename or '.' not in filename:
            # Try to get content type from headers
            content_type = response.headers.get('Content-Type', '')
            if 'video' in content_type:
                filename = 'downloaded_video.mp4'
            elif 'image' in content_type:
                filename = 'downloaded_image.jpg'
            else:
                filename = 'downloaded_media'
        
        # Create the full path
        if directory:
            full_path = os.path.join(directory, filename)
        else:
            full_path = filename
        
        # Write the content to a file in binary mode
        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        
        debug_print(f"Downloaded {full_path} successfully.")
        return full_path
    else:
        debug_print(f"Failed to download media. Status code: {response.status_code}")
        return None


if __name__ == "__main__":
    TEST_SCRIPT = """<HOOK>Tumult in Myanmar's political landscape as the military government pushes for national elections amid growing pressure from domestic and foreign influences.</HOOK>

<BODY>Myanmar's military government faces mounting pressure to hold elections, with China supporting the move to maintain influence. Meanwhile, internal dissent grows within junta ranks, including among elite forces loyal to General Min Aung Hlaing.
Civilians increasingly demand democratic accountability amid ongoing civil war. ASEAN members are divided but generally oppose the elections, concerned about regional stability and Chinese influence.

The People's Defence Force (PDF) has targeted civilians involved in election preparations, arresting teachers and others in southern regions, creating a climate of fear. Some observers, like Zaw Kyaw from the National Union of Goldberg and Assistance League, believe the military will eventually collapse due to low morale regardless of election outcomes.</BODY>
<OUTRO>Who will be next in line to lead Myanmar? Will the junta hold until the end, or will democracy prevail? The fate of this small nation, and its people, hangs in the balance. What do you think? Lets discuss in the comments below.</OUTRO>"""

    test_keywords = [['military', 'government'], ['civilian', 'demand'], ['regional', 'voter'], ['military', 'collapse'], ['junta', 'and'], ['image', 'enhancement']]