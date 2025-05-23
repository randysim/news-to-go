from dotenv import load_dotenv
from ..video.generate_video import gather_video_resources, save_config, construct_video
from ..scraper.scrape_generic import scrape_generic
import os

if __name__ == "__main__":
    load_dotenv()

    print("Running tests...")

    test_url = "https://apnews.com/article/thailand-earthquake-bangkok-4fce87aced74b1fc0cf260fb5454d353"
    output_dir = "tests"

    print("Scraping generic...")
    title, content = scrape_generic(test_url)
    resources = gather_video_resources(title, content, should_generate_keywords=False, directory=output_dir)

    # SAVE CONFIG
    path = save_config(*resources, save_dir=os.path.join(output_dir, "configs"))
    print(f"Config saved to {path}")