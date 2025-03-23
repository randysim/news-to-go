# news-to-go backend

## Requirements

- python -m venv venv
- pip install -r requirements.txt
- have ollama installed + ollama pull <model-name> (ex: deepseek-r1)
- have ffmpeg installed (sudo apt install ffmpeg)
- have firefox.geckodriver installed at /snap/bin/firefox.geckodriver (whereis firefox.geckodriver). Can install firefox snap on WSL using ``sudo snap install firefox``

## Windows + WSL

If you are running ollama on windows and the backend on WSL

Open windows powershell
- setx OLLAMA_HOST "0.0.0.0" /m
- setx OLLAMA_ORIGINS "*" /m

This will allow WSL to access the OLLAMA api. Make sure to replace localhost with your windows computers IPv4

Address as WSL and windows have two different network configurations.

## Run individual scripts as test

``python -m modules.folder.script_name`` without the .py

## .env file format
```
DRIVER_PATH=<PATH TO WEBDRIVER>
PEXELS_API_KEY=
OLLAMA_IP=<IP OF COMPUTER YOU ARE HOSTING OR LOCALHOST IF SAME COMPUTER>
OLLAMA_MODEL=<OLLAMA LLM MODEL>
ERROR_DIRECTORY=resource/error
```

## font

In the fonts folder, add fonts. Then, in generate_video.py, update the font moviepy uses for the captions