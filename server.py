from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv
import httpx
import os
import json

load_dotenv()

app = FastAPI(title="ChatGPT Clone")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant"
ALLOWED_MODELS = {
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama-4-scout-17b-16e-instruct",
    "llama-4-maverick-17b-128e-instruct",
    "qwen-qwq-32b",
}

@app.get("/", response_class=HTMLResponse)
async def home():
    import os
    path = os.path.join(os.path.dirname(__file__), "static/index.html")
    with open(path, encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", DEFAULT_MODEL)
    if not isinstance(messages, list):
        messages = []
    if model not in ALLOWED_MODELS:
        model = DEFAULT_MODEL

    if not GROQ_API_KEY:
        return StreamingResponse(
            iter(["[Server error] GROQ_API_KEY is missing."]),
            media_type="text/plain"
        )

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "max_tokens": 1024,
                "temperature": 0.7,
            },
        )
        if resp.status_code >= 400:
            return StreamingResponse(
                iter([f"[Provider error {resp.status_code}] {resp.text}"]),
                media_type="text/plain"
            )
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]
        return StreamingResponse(iter([reply]), media_type="text/plain")
