# ChatGPT Clone (Professional Starter)

A more professional **ChatGPT-style** starter with:
- FastAPI backend
- Streaming chat responses
- Groq provider integration
- Multi-chat sidebar (create/switch/delete)
- Local chat history persistence
- Model picker UI
- Health endpoint for deployment checks

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

Tip: `.env` is auto-loaded by `python-dotenv` in `server.py`, so you can usually run `uvicorn server:app --reload` directly without manual `export`.

## 2) Docker

```bash
docker build -t chatgpt-clone .
docker run -e GROQ_API_KEY=your_key -p 8000:8000 chatgpt-clone
```

## 3) Verify deployed API key (safe checks)

Check app health and whether API key is configured:

```bash
curl -s http://127.0.0.1:8000/health
```

Check environment variable exists without printing full key:

```bash
python3 -c 'import os;k=os.getenv("GROQ_API_KEY","");print("set" if k else "missing", "len=", len(k), "suffix=", k[-4:] if k else "")'
```

## 4) Security note

If you shared your API key publicly, revoke it immediately and create a new one in Groq console.

## 5) Notes

- This is a **ChatGPT-like UI**, not an official OpenAI frontend clone.
- To fully match ChatGPT features (auth, files, tools, projects, voice), add DB + accounts + feature modules.
