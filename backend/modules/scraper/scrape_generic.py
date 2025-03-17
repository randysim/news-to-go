from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

def scrape_generic(driver, url):
    driver.get(url)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "p"))
    )

    # Get title
    title = driver.title

    # get parent element
    """
    paragraph_elements = driver.find_elements(By.TAG_NAME, "p")
    initial_paragraph = paragraph_elements[len(paragraph_elements) // 2] # get the middle paragraph
    parent_element = initial_paragraph.find_element(By.XPATH, "./../..")
    parent_html = parent_element.get_attribute("outerHTML")"
    """
    parent_html = driver.page_source
    
    # parse article
    soup = BeautifulSoup(parent_html, "html.parser")
    tags = soup.find_all(["p", "ul"])

    article_content = ""
    for tag in tags:
        if tag.name == "p":
            p_content = tag.text.strip()

            # AP News Filters
            if p_content.startswith("▶"):
                continue

            # Copyright filters
            copyright_string = f"Copyright {datetime.today().year}"
            if copyright_string in p_content:
                continue
            
            if p_content:
                article_content += p_content + "\n"
        elif tag.name == "ul":
            for li in tag.find_all("li"):
                # if li contains a <a>, skip
                has_only_text = all(isinstance(content, NavigableString) for content in li.contents)
    
                if not has_only_text:
                    continue

                list_item_content = li.text.strip()
                if list_item_content:
                    article_content += "- " + li.text.strip() + "\n"
    
    # replace odd characters
    character_replacements = {
        "“": "\"",
        "”": "\"",
        "’": "'",
        "‘": "'",
        "—": ", ",
        "…": "...",
        "\n\n": "\n",
        "\t": "",
        "  ": ""
    }

    for key, value in character_replacements.items():
        article_content = article_content.replace(key, value)
    
    return title, article_content
        

if __name__ == "__main__":
    DRIVER_PATH = "/snap/bin/firefox.geckodriver"
    DRIVER = Service(executable_path=DRIVER_PATH)
    firefox_options = Options()

    user_agents = ["Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"]
    firefox_options.add_argument(f"user-agent={user_agents[0]}")
    firefox_options.add_argument("--headless")

    driver = webdriver.Firefox(service=DRIVER, options=firefox_options)
    driver.maximize_window()

    test_articles = {
        "bbc": "https://www.bbc.com/news/articles/c9wpq0g10xjo",
        "ap": "https://apnews.com/article/trump-venezuela-el-salvador-immigration-dd4f61999f85c4dd8bcaba7d4fc7c9af",
        "aljazeera": "https://www.aljazeera.com/news/2025/3/15/inch-by-inch-myanmar-rebels-close-in-on-key-military-base-in-chin-state",
        "indiatimes": "https://economictimes.indiatimes.com/news/india/inside-the-illicit-trade-of-exotic-animals-from-myanmar-to-india/articleshow/110425853.cms?from=mdr",
        "vaticannews": "https://www.vaticannews.va/en/world/news/2025-03/myanmars-immense-suffering-worsens-amid-global-aid-cuts.html",
        "nytimes": "https://www.nytimes.com/2025/03/17/us/politics/bongino-patel-fbi-trump.html",
        "npr": "https://www.npr.org/2025/03/17/nx-s1-5330840/trump-kennedy-center-honorees-board",
        "politico": "https://www.politico.com/news/2025/03/17/rasha-alawieh-deportation-026038"
    }

    TEST_URL = test_articles.get("npr")
    print(f"Fetching URL {TEST_URL}")

    title, content = scrape_generic(driver, TEST_URL)
    print(f"Retrieved Article {title}")

    # Write to file in tests/
    if not os.path.exists("tests"):
        os.makedirs("tests")
    
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d:%H:%M:%S")
    file_name = f"{date_string}_{title}.txt"
    with open(f"tests/{file_name}", "w") as f:
        f.write(content)