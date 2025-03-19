from ..video.generate_video import load_config, construct_video

if __name__ == "__main__":
    config_path = "tests/configs/i_want_to_kill_these_dogs_question_of_whether_to_cull_strays_divides_yangon__cities__the_guardian_config.json"
    config = load_config(config_path)

    print("Constructing video from config...")
    construct_video(*config)