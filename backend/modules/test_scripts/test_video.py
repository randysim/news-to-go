from dotenv import load_dotenv
from ..video.generate_video import gather_video_resources, construct_video
from ..scraper.scrape_generic import scrape_generic
import os

if __name__ == "__main__":
    load_dotenv()

    print("Running tests...")

    test_url = "https://www.aljazeera.com/news/2025/3/15/inch-by-inch-myanmar-rebels-close-in-on-key-military-base-in-chin-state"
    output_dir = "tests"

    print("Scraping generic...")
    title, content = scrape_generic(test_url)
    resources = gather_video_resources(title, content, output_dir)

    # LOG RESOURCES
    with open("tests/resources.txt", "w") as f:
        f.write(str(resources))

    construct_video(*resources)