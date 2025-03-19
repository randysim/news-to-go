from ..video.generate_video import load_config, construct_video

if __name__ == "__main__":
    config_path = "tests/configs/inch_by_inch_myanmar_rebels_close_in_on_key_military_base_in_chin_state__military_news__al_jazeera_config.json"
    config = load_config(config_path)

    print("Constructing video from config...")
    construct_video(*config)