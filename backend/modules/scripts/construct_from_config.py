from ..video.generate_video import load_config, construct_video

if __name__ == "__main__":
    config_path = "tests/configs/violent_earthquakes_rock_thailand_and_myanmar__ap_news_config.json"
    config = load_config(config_path)

    print("Constructing video from config...")
    construct_video(*config)