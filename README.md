# ChatGPT Clone (Professional Starter)

A cleaner, production-ready starter that mimics the **ChatGPT-style experience** with:
- FastAPI backend
- Streaming chat responses
- Groq provider integration
- Multi-chat sidebar
- Local chat history persistence
- Model picker UI

## 1) Clone and setup

```bash
git clone https://github.com/rintuchowdory/chatgpt-clone.git
cd chatgpt-clone
cp .env.example .env
# add your GROQ_API_KEY to .env
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload
```

Open: http://127.0.0.1:8000

## 2) Docker

```bash
docker build -t chatgpt-clone .
docker run -e GROQ_API_KEY=your_key -p 8000:8000 chatgpt-clone
```

## 3) Notes

- This is a **ChatGPT-like UI**, not an official OpenAI frontend clone.
- To fully match ChatGPT features (auth, files, tools, projects, voice, etc.), add persistent DB, user accounts, and feature modules.
- You can switch models from the top-right selector in the UI.

## 4) Free Groq API key

https://console.groq.com
