# ChatGPT Clone

FastAPI + Groq API (LLaMA3) with streaming and dark UI.

## Run locally
cp .env.example .env
# add your GROQ_API_KEY to .env
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload

## Docker
docker build -t chatgpt-clone .
docker run -e GROQ_API_KEY=your_key -p 8000:8000 chatgpt-clone

## Get free Groq API key
https://console.groq.com
