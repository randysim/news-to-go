from ..video.generate_video import load_config, construct_video

if __name__ == "__main__":
    config_path = "tests/configs/dharma_dogs_buddhist_chants_calm_stray_myanmar_mutts__environment__the_jakarta_post_config.json"
    config = load_config(config_path)

    print("Constructing video from config...")
    construct_video(*config)