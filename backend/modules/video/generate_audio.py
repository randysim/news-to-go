import os
from .clean import get_within_tags
from yapper import Yapper, PiperSpeaker, PiperVoiceUK

vanilla_yapper = Yapper()
speaker = PiperSpeaker(
    voice=PiperVoiceUK.SOUTHERN_ENGLISH_FEMALE
)

def generate_audio_file(text, name, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    speaker.text_to_wave(text, f"{directory}/{name}.wav")

    return f"{directory}/{name}.wav"

def generate_audio_from_script(script, name, directory):
    hook = get_within_tags("HOOK", script)
    body = get_within_tags("BODY", script)
    outro = get_within_tags("OUTRO", script)

    return generate_audio_file(f"{hook} {body} {outro}", name, directory)

if __name__ == "__main__":
    TEST_SCRIPT = """<HOOK>Tumult in Myanmar's political landscape as the military government pushes for national elections amid growing pressure from domestic and foreign influences.</HOOK>

<BODY>Myanmar's military government faces mounting pressure to hold elections, with China supporting the move to maintain influence. Meanwhile, internal dissent grows within junta ranks, including among elite forces loyal to General Min Aung Hlaing.
Civilians increasingly demand democratic accountability amid ongoing civil war. ASEAN members are divided but generally oppose the elections, concerned about regional stability and Chinese influence.

The People's Defence Force (PDF) has targeted civilians involved in election preparations, arresting teachers and others in southern regions, creating a climate of fear. Some observers, like Zaw Kyaw from the National Union of Goldberg and Assistance League, believe the military will eventually collapse due to low morale regardless of election outcomes.</BODY>
<OUTRO>Who will be next in line to lead Myanmar? Will the junta hold until the end, or will democracy prevail? The fate of this small nation, and its people, hangs in the balance. What do you think? Lets discuss in the comments below.</OUTRO>"""

    audio_files = generate_audio_from_script(TEST_SCRIPT, "test_script_53242", "audio")