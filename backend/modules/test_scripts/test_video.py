from dotenv import load_dotenv
from ..video.generate_images import search_media, download_media
from ..video.generate_video import get_sentence_starts
from ..video.generate_audio import generate_audio_from_script
from ..video.generate_captions import fix_captions, generate_captions
import os

if __name__ == "__main__":
    load_dotenv()

    print("Running tests...")

    TEST_SCRIPT = """<HOOK>Tumult in Myanmar's political landscape as the military government pushes for national elections amid growing pressure from domestic and foreign influences.</HOOK>

<BODY>Myanmar's military government faces mounting pressure to hold elections, with China supporting the move to maintain influence. Meanwhile, internal dissent grows within junta ranks, including among elite forces loyal to General Min Aung Hlaing.
Civilians increasingly demand democratic accountability amid ongoing civil war. ASEAN members are divided but generally oppose the elections, concerned about regional stability and Chinese influence.

The People's Defence Force (PDF) has targeted civilians involved in election preparations, arresting teachers and others in southern regions, creating a climate of fear. Some observers, like Zaw Kyaw from the National Union of Goldberg and Assistance League, believe the military will eventually collapse due to low morale regardless of election outcomes.</BODY>
<OUTRO>Who will be next in line to lead Myanmar? Will the junta hold until the end, or will democracy prevail? The fate of this small nation, and its people, hangs in the balance. What do you think? Lets discuss in the comments below.</OUTRO>"""

    resource_directory = "resource"
    script_name = "test_myanmar"
    audio_file = generate_audio_from_script(TEST_SCRIPT, script_name, os.path.join(resource_directory, "audio"))
    captions = fix_captions(generate_captions(audio_file), TEST_SCRIPT)
    sentence_starts = get_sentence_starts(TEST_SCRIPT, captions)
    print(f"Found Sentence Starts:\n{sentence_starts}")