from dotenv import load_dotenv
from ..video.generate_images import search_media, download_media

if __name__ == "__main__":
    load_dotenv()

    print("Running tests...")

    TEST_SCRIPT = """<HOOK>Tumult in Myanmar's political landscape as the military government pushes for national elections amid growing pressure from domestic and foreign influences.</HOOK>

<BODY>Myanmar's military government faces mounting pressure to hold elections, with China supporting the move to maintain influence. Meanwhile, internal dissent grows within junta ranks, including among elite forces loyal to General Min Aung Hlaing.
Civilians increasingly demand democratic accountability amid ongoing civil war. ASEAN members are divided but generally oppose the elections, concerned about regional stability and Chinese influence.

The People's Defence Force (PDF) has targeted civilians involved in election preparations, arresting teachers and others in southern regions, creating a climate of fear. Some observers, like Zaw Kyaw from the National Union of Goldberg and Assistance League, believe the military will eventually collapse due to low morale regardless of election outcomes.</BODY>
<OUTRO>Who will be next in line to lead Myanmar? Will the junta hold until the end, or will democracy prevail? The fate of this small nation, and its people, hangs in the balance. What do you think? Lets discuss in the comments below.</OUTRO>"""

    test_keywords = [['military', 'government'], ['civilian', 'demand'], ['regional', 'voter'], ['military', 'collapse'], ['junta', 'and'], ['image', 'enhancement']]

    media_url = search_media(test_keywords[0])
    download_media(media_url, "resource/media")