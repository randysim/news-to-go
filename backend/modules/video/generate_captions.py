import whisper
import os

from .clean import get_within_tags, clean_double_space

model = whisper.load_model("medium")

def generate_captions(audio_file):
    result = model.transcribe(audio_file, word_timestamps=True)

    captions = []
    for segment in result["segments"]:
        for word in segment["words"]:
            start = word["start"].item() if hasattr(word["start"], "item") else word["start"]
            end = word["end"].item() if hasattr(word["end"], "item") else word["end"]
            captions.append([word["word"].strip(), start, end])
    
    return captions

def fix_captions(captions, script):
    script_text = get_within_tags("HOOK", script) + " " + get_within_tags("BODY", script) + " " + get_within_tags("OUTRO", script)
    script_text = script_text.replace("\n", " ")
    
    script_text = clean_double_space(script_text)
    
    script_words = script_text.split(" ")
    
    fixed_captions = []
    script_idx = 0
    caption_idx = 0
    
    while caption_idx < len(captions) and script_idx < len(script_words):
        current_caption = captions[caption_idx]
        current_script_word = script_words[script_idx].strip()
        
        # Case 1: Words match exactly
        if current_caption[0].lower() == current_script_word.lower():
            fixed_captions.append(current_caption)
            script_idx += 1
            caption_idx += 1
            continue
        
        # Case 2: Words don't match - need to find next matching point
        # Try to find the next matching word in both script and captions
        next_script_match = find_next_match(script_words, script_idx, captions, caption_idx)
        
        if next_script_match:
            script_match_idx, caption_match_idx = next_script_match
            
            # Combine mismatched words from script
            combined_script_word = " ".join(script_words[script_idx:script_match_idx])
            
            # Get timing from the caption(s) we're replacing
            start_time = captions[caption_idx][1]
            end_time = captions[caption_match_idx-1][2]
            
            # Create new fixed caption with correct script word(s) but caption timing
            fixed_captions.append([combined_script_word, start_time, end_time])
            
            # Update indices
            script_idx = script_match_idx
            caption_idx = caption_match_idx
        else:
            # If no more matches found, just add the remaining captions as is
            fixed_captions.append(current_caption)
            script_idx += 1
            caption_idx += 1
    
    # Add any remaining captions
    while caption_idx < len(captions):
        fixed_captions.append(captions[caption_idx])
        caption_idx += 1
    
    return fixed_captions

def find_next_match(script_words, script_idx, captions, caption_idx, max_lookahead=5):
    """Find the next point where script and captions match again, with limited lookahead."""
    # Limit how far ahead we look to avoid matching with words much later in the script
    max_script_idx = min(script_idx + max_lookahead, len(script_words))
    max_caption_idx = min(caption_idx + max_lookahead, len(captions))
    
    for s_idx in range(script_idx + 1, max_script_idx):
        for c_idx in range(caption_idx + 1, max_caption_idx):
            if script_words[s_idx].strip().lower() == captions[c_idx][0].lower():
                # Found a match within our lookahead window
                return s_idx, c_idx
    
    # No match found within lookahead window
    return None

if __name__ == "__main__":
    TEST_AUDIO = "audio/test_script_53242.wav"

    TEST_SCRIPT = """<HOOK>Tumult in Myanmar's political landscape as the military government pushes for national elections amid growing pressure from domestic and foreign influences.</HOOK>

<BODY>Myanmar's military government faces mounting pressure to hold elections, with China supporting the move to maintain influence. Meanwhile, internal dissent grows within junta ranks, including among elite forces loyal to General Min Aung Hlaing.
Civilians increasingly demand democratic accountability amid ongoing civil war. ASEAN members are divided but generally oppose the elections, concerned about regional stability and Chinese influence.

The People's Defence Force (PDF) has targeted civilians involved in election preparations, arresting teachers and others in southern regions, creating a climate of fear. Some observers, like Zaw Kyaw from the National Union of Goldberg and Assistance League, believe the military will eventually collapse due to low morale regardless of election outcomes.</BODY>
<OUTRO>Who will be next in line to lead Myanmar? Will the junta hold until the end, or will democracy prevail? The fate of this small nation, and its people, hangs in the balance. What do you think? Lets discuss in the comments below.</OUTRO>"""

    fixed_captions = fix_captions(generate_captions(TEST_AUDIO), TEST_SCRIPT)

    if not os.path.exists("tests/captions"):
        os.makedirs("tests/captions")
    
    with open("tests/captions/test_script_53242.txt", "w") as f:
        for caption in fixed_captions:
            f.write(f"{caption[0]}:{caption[1]}:{caption[2]}\n")