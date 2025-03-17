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