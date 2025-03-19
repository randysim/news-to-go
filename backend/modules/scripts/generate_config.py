from dotenv import load_dotenv
from ..video.generate_video import gather_video_resources, save_config, construct_video
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

    # SAVE CONFIG
    path = save_config(*resources, save_dir=os.path.join(output_dir, "configs"))
    print(f"Config saved to {path}")