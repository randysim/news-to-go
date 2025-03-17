# news-to-go backend

## Requirements

- python -m venv venv
- pip install requirements.txt
- have ollama run llama3.2
- have firefox.geckodriver installed at /snap/bin/firefox.geckodriver (whereis firefox.geckodriver)

## Windows + WSL

If you are running ollama on windows and the backend on WSL

Open windows powershell
- setx OLLAMA_HOST "0.0.0.0" /m
- setx OLLAMA_ORIGINS "*" /m

This will allow WSL to access the OLLAMA api. Make sure to replace localhost with your windows computers IPv4

Address as WSL and windows have two different network configurations.

## Fix preload_models error

- Click into preload_models and search for "torch.load". On that line, set weights_only=False in the function call.