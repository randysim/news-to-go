def clean_think(text):
    return text.split("</think>")[1].strip()

def clean_bullet_points(text):
    cleaned_text = ""
    for line in text.split("\n"):
        # check if line starts with a number
        if not line:
            continue

        if line[0].isdigit():
            cleaned_text += line[2:].strip() + "\n"
        elif line[0] == "-" or line[1] == "-":
            cleaned_text += line[2:].strip() + "\n"
        else:
            cleaned_text += line.strip() + "\n"
    return cleaned_text.strip()

def clean_characters(text):
    blacklisted = ["“", "”", "’", "‘", "…", "\t", "*"]
    for char in blacklisted:
        text = text.replace(char, "")
    return text

def clean_double_newlines(text):
    while "\n\n" in text:
        text = text.replace("\n\n", "\n")
    return text

def clean_em_dashes(text):
    return text.replace("—", ", ")

def clean_double_space(text):
    return text.replace("  ", " ")

def clean_colons(text):
    cleaned_text = ""
    for line in text.split("\n"):
        colon_index = line.find(":")
        if colon_index != -1 and colon_index < 35:
            cleaned_text += line.split(":")[1].strip() + "\n"
        else:
            cleaned_text += line.strip() + "\n"
    return cleaned_text.strip()

def get_within_tags(tag, text):
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start_index = text.find(start_tag)
    end_index = text.find(end_tag)
    return text[start_index + len(start_tag):end_index].strip()

def clean_html_tags(text):
    cleaned_text = ""
    while "<" in text:
        start_index = text.find("<")
        end_index = text.find(">")
        if end_index == -1:
            return text
        
        cleaned_text += text[:start_index]
        text = text[end_index + 1:]

        
    cleaned_text += text
    return cleaned_text.strip()

def clean_non_ascii(text):
    return ''.join(i for i in text if ord(i) < 128)

def clean_main_quotes(text):
    if text.startswith("\""):
        text = text[1:]
    if text.endswith("\""):
        text = text[:-1]
    return text