# NexusAI — ChatGPT Clone (Professional)

A production-ready ChatGPT-style chat application with real streaming, 3D animations, and modern Groq models.

## ✨ Features

- **Real SSE Streaming** — Token-by-token responses from Groq, not fake typing
- **3D Animations** — Rotating 3D logo, floating background particles, 3D message entrance, interactive 3D tilt on suggestions
- **Dark / Light Theme** — Toggle with localStorage persistence
- **Code Highlighting** — Syntax highlighting via highlight.js for all code blocks
- **Chat Export** — Download conversations as JSON or Markdown
- **Multi-Chat Sidebar** — Multiple conversations with local persistence
- **Voice Input & Talk Mode** — Speech recognition + TTS with a 3D orb interface
- **Stop / Regenerate** — Stop generation mid-stream or regenerate responses
- **Current Groq Models** — GPT-OSS 120B/20B, Compound (agentic), Qwen 3.6

## 1) Quick Start

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
docker build -t nexusai .
docker run -e GROQ_API_KEY=your_key -p 8000:8000 nexusai
```

## 3) Vercel Deployment

The included `vercel.json` routes all traffic through the FastAPI server. Deploy with:

```bash
vercel --prod
```

Make sure to set `GROQ_API_KEY` as an environment variable in Vercel.

## 4) Available Models

| Model | Speed | Context | Best For |
|-------|-------|---------|----------|
| GPT-OSS 120B | ~500 t/s | 131K | Flagship — reasoning, tools |
| GPT-OSS 20B | ~1000 t/s | 131K | Fast responses, great latency |
| Compound | ~450 t/s | 131K | Agentic — web search + code exec |
| Compound Mini | ~450 t/s | 131K | Lightweight agentic tasks |
| Qwen 3.6 27B | ~500 t/s | 131K | Reasoning (preview) |

## 5) Keyboard Shortcuts

- `Enter` — Send message
- `Shift + Enter` — New line
- `Ctrl/Cmd + K` — Toggle Talk Mode

## 6) Free Groq API Key

https://console.groq.com

## Notes

- This is a ChatGPT-like UI, not an official OpenAI frontend.
- Chat history is stored in localStorage (per-session).
- For production use, add authentication and a persistent database.
