import os
from yapper import Yapper, PiperSpeaker, PiperVoiceUK

vanilla_yapper = Yapper()
speaker = PiperSpeaker(
    voice=PiperVoiceUK.ALAN
)


def get_within_tags(tag, text):
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start_index = text.find(start_tag)
    end_index = text.find(end_tag)
    return text[start_index + len(start_tag):end_index].strip()

def generate_audio_file(text, name, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    speaker.text_to_wave(text, f"{directory}/{name}.wav")

    return f"{directory}/{name}.wav"

def generate_audio_from_script(script, name, directory):
    hook = get_within_tags("HOOK", script)
    body = get_within_tags("BODY", script)
    outro = get_within_tags("OUTRO", script)

    sentences = hook.split(".") + body.split(".") + outro.split(".")
    audio_files = []

    sub_directory = f"{directory}/{name}"
    i = 0
    while os.path.exists(sub_directory):
        i += 1
        sub_directory = f"{directory}/{name}_{i}"
    os.mkdir(sub_directory)

    for sentence in sentences:
        if not sentence:
            continue

        sentence = sentence.strip()
        audio_files.append((sentence, generate_audio_file(sentence, f"{name}_{len(audio_files)}", sub_directory)))

    return audio_files

if __name__ == "__main__":
    TEST_SCRIPT = """<HOOK>Tumult in Myanmar's political landscape as the military government pushes for national elections amid growing pressure from domestic and foreign influences.</HOOK>

<BODY>Myanmar's military government faces mounting pressure to hold elections, with China supporting the move to maintain influence. Meanwhile, internal dissent grows within junta ranks, including among elite forces loyal to General Min Aung Hlaing.
Civilians increasingly demand democratic accountability amid ongoing civil war. ASEAN members are divided but generally oppose the elections, concerned about regional stability and Chinese influence.

The People's Defence Force (PDF) has targeted civilians involved in election preparations, arresting teachers and others in southern regions, creating a climate of fear. Some observers, like Zaw Kyaw from the National Union of Goldberg and Assistance League, believe the military will eventually collapse due to low morale regardless of election outcomes.</BODY>
<OUTRO>Who will be next in line to lead Myanmar? Will the junta hold until the end, or will democracy prevail? The fate of this small nation, and its people, hangs in the balance. What do you think? Lets discuss in the comments below.</OUTRO>"""

    audio_files = generate_audio_file(TEST_SCRIPT, "test_script_53242", "audio")
    