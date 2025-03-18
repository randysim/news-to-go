from ollama import Client
from .clean import clean_think, clean_bullet_points, clean_characters, clean_double_newlines, clean_em_dashes, clean_double_space, clean_colons, get_within_tags, clean_html_tags, clean_non_ascii, clean_main_quotes
import os

MODELS = ["llama3.2", "deepseek-r1", "mistral"]

client = Client(
    host="http://172.22.160.1:11434"
)

MODEL = MODELS[1]
SUMMARY_SYSTEM_MESSAGE = """You are a helpful summarizer. You will be given text to summarize into a paragraph. Write in complete english sentences and avoid referencing the text itself (e.g. phrases like "the text states" or "the text mentions")."""

SCRIPT_SYSTEM_MESSAGE = """You are a video script writer. You will be given a paragraph summary of a topic. You must turn the summary into a script in english for a video.
It will have 3 parts, the HOOK, BODY, and OUTRO, each section marked by tags.
The HOOK is the opening line to grab attention. The BODY is a cohesive paragraph. The OUTRO is a closing statement or a question or call to action.
Format the final script as such:
<HOOK> {HOOK} </HOOK>
<BODY> {BODY} </BODY>
<OUTRO> {OUTRO} </OUTRO>"""



def is_valid_script(text):
    return "<HOOK>" in text and "<BODY>" in text and "<OUTRO>" in text and "</HOOK>" in text and "</BODY>" in text and "</OUTRO>" in text

def is_play_script(text):
    return "[" in text and "]" in text

def generate_script(news_content):
    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SUMMARY_SYSTEM_MESSAGE
            },
            {
                "role": "user",
                "content": f"Summarize the following news article into a paragraph:\n{news_content}"
            }
        ]
    )

    default_summary = ""
    default_script = ""

    dirty_summary = response['message']['content']
    default_summary = dirty_summary
    # Get rid of stuff within <think>
    dirty_summary = clean_think(dirty_summary)
    dirty_summary = clean_characters(dirty_summary)
    dirty_summary = clean_bullet_points(dirty_summary)
    dirty_summary = clean_non_ascii(dirty_summary)
    dirty_summary = clean_em_dashes(dirty_summary)
    dirty_summary = clean_colons(dirty_summary)
    dirty_summary = clean_double_newlines(dirty_summary)

    article_summary = clean_main_quotes(clean_double_space(dirty_summary))

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SCRIPT_SYSTEM_MESSAGE
            },
            {
                "role": "user",
                "content": f"Turn the following summary into a video script:\n{article_summary}"
            }
        ]
    )

    script = response['message']['content']
    while not is_valid_script(script) or is_play_script(script):
        print("Regenerating invalid script...")
        response = client.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SCRIPT_SYSTEM_MESSAGE
                },
                {
                    "role": "user",
                    "content": f"Turn the following summary into a video script:\n{article_summary}"
                }
            ]
        )
        script = response['message']['content']

    default_script = script
    script = clean_think(script)
    script = clean_bullet_points(script)
    script = clean_characters(script)
    script = clean_colons(script)
    script = clean_em_dashes(script)
    script = clean_non_ascii(script)
    script = clean_double_space(script)
    script = clean_double_newlines(script)
    
    HOOK = clean_main_quotes(clean_html_tags(get_within_tags("HOOK", script)))
    BODY = clean_main_quotes(clean_html_tags(get_within_tags("BODY", script)))
    OUTRO = clean_main_quotes(clean_html_tags(get_within_tags("OUTRO", script)))

    script = f"<HOOK>{HOOK}</HOOK>\n<BODY>{BODY}</BODY>\n<OUTRO>{OUTRO}</OUTRO>"

    return article_summary, script, default_summary, default_script

def generate_script_file(news_content, script_name, directory):
    summary, script, default_summary, default_script = generate_script(news_content)
    with open(f"{directory}/{script_name}.txt", "w") as f:
        f.write(f"SUMMARY:\n{summary}\n\nSCRIPT:\n{script}")
    with open(f"{directory}/default_{script_name}.txt", "w") as f:
        f.write(f"SUMMARY:\n{default_summary}\n\nSCRIPT:\n{default_script}")

if __name__ == "__main__":
    print("Attempting to generate scripts...")
    PATH_TO_NEWS = "/home/randy/projects/news-to-go/backend/tests/test_news.txt"

    if not os.path.exists("tests"):
        os.makedirs("tests")
    
    if not os.path.exists("tests/scripts"):
        os.makedirs("tests/scripts")

    news_content = ""
    with open(PATH_TO_NEWS, "r") as file:
        news_content = file.read()
        
    # write script to file
    for i in range(2):
        script_name = f"script_{i}"
        generate_script_file(news_content, script_name, "tests/scripts")
        print(f"Generated script {script_name}")
    print("Done generating scripts")
