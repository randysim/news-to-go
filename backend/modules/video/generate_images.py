import re
import os
import requests
from ollama import Client
from .clean import get_within_tags, clean_think, clean_double_newlines, clean_double_space, clean_main_quotes, clean_non_ascii, clean_colons, clean_html_tags

client = Client(
    host=f"http://{os.getenv('OLLAMA_IP')}:11434"
)

MODEL = os.getenv("OLLAMA_MODEL")

KEYWORD_MESSAGE = """You are a specialized keyword generator for image searches. When given text, generate ONE highly specific two-word keyword phrase that precisely captures the unique technical context of the provided content.

Avoid generic terms like "action words" or broad category nouns. Instead, focus on technical terminology, specific concepts, or distinctive elements from the text.

Your keyword should be:
- Exactly two words
- Highly specific to the technical subject matter
- Useful for finding relevant technical images
- Focused on distinctive elements rather than generic concepts

Format your response as: <KEYWORD>{your two-word keyword}</KEYWORD>
"""

def generate_fragments(script, image_every=2):
    text = get_within_tags("HOOK", script) + " " + get_within_tags("BODY", script) + " " + get_within_tags("OUTRO", script)
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
    return "<KEYWORD>" in text and "</KEYWORD>" in text

def generate_keyword(text):
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

def generate_keywords(script, every_n_sentences=2):
    fragments = generate_fragments(script, image_every=every_n_sentences)

    keywords = []

    for fragment in fragments:
        keywords.append(generate_keyword(fragment))
    
    return keywords

def search_media(keyword, nth=0):
    # Base URLs for Pexels API
    VIDEO_SEARCH_URL = 'https://api.pexels.com/videos/search'
    IMAGE_SEARCH_URL = 'https://api.pexels.com/v1/search'

    # Combine keywords for the search
    combined_keywords = ' '.join(keyword)

    # Headers for the API request
    headers = {
        'Authorization': os.getenv("PEXELS_API_KEY")
    }

    # Step 1: Search for a video with combined keywords
    response = requests.get(VIDEO_SEARCH_URL, headers=headers, params={'query': combined_keywords, 'per_page': nth+1})
    if response.status_code == 200:
        data = response.json()
        if data.get('videos') and len(data['videos']) > nth:
            # Get the nth video and its highest quality file
            video_files = data['videos'][nth]['video_files']
            if video_files:
                # Sort by height (resolution) in descending order and get the first one
                video_files.sort(key=lambda x: x.get('height', 0), reverse=True)
                return video_files[0]['link']

    # Step 2: Search for a video with the first keyword only
    response = requests.get(VIDEO_SEARCH_URL, headers=headers, params={'query': keyword[0], 'per_page': nth+1})
    if response.status_code == 200:
        data = response.json()
        if data.get('videos') and len(data['videos']) > nth:
            video_files = data['videos'][nth]['video_files']
            if video_files:
                video_files.sort(key=lambda x: x.get('height', 0), reverse=True)
                return video_files[0]['link']

    # Step 3: Search for an image with combined keywords
    response = requests.get(IMAGE_SEARCH_URL, headers=headers, params={'query': combined_keywords, 'per_page': nth+1})
    if response.status_code == 200:
        data = response.json()
        if data.get('photos') and len(data['photos']) > nth:
            return data['photos'][nth]['src']['original']

    # Step 4: Search for an image with the first keyword only
    response = requests.get(IMAGE_SEARCH_URL, headers=headers, params={'query': keyword[0], 'per_page': nth+1})
    if response.status_code == 200:
        data = response.json()
        if data.get('photos') and len(data['photos']) > nth:
            return data['photos'][nth]['src']['original']

    # Step 5: Return a default image if all searches fail
    return 'https://images.pexels.com/photos/281260/pexels-photo-281260.jpeg'




if __name__ == "__main__":
    TEST_SCRIPT = """<HOOK>Tumult in Myanmar's political landscape as the military government pushes for national elections amid growing pressure from domestic and foreign influences.</HOOK>

<BODY>Myanmar's military government faces mounting pressure to hold elections, with China supporting the move to maintain influence. Meanwhile, internal dissent grows within junta ranks, including among elite forces loyal to General Min Aung Hlaing.
Civilians increasingly demand democratic accountability amid ongoing civil war. ASEAN members are divided but generally oppose the elections, concerned about regional stability and Chinese influence.

The People's Defence Force (PDF) has targeted civilians involved in election preparations, arresting teachers and others in southern regions, creating a climate of fear. Some observers, like Zaw Kyaw from the National Union of Goldberg and Assistance League, believe the military will eventually collapse due to low morale regardless of election outcomes.</BODY>
<OUTRO>Who will be next in line to lead Myanmar? Will the junta hold until the end, or will democracy prevail? The fate of this small nation, and its people, hangs in the balance. What do you think? Lets discuss in the comments below.</OUTRO>"""

    test_keywords = [['military', 'government'], ['civilian', 'demand'], ['regional', 'voter'], ['military', 'collapse'], ['junta', 'and'], ['image', 'enhancement']]