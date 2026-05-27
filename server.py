from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os
import json

app = FastAPI(title="ChatGPT Clone")
app.mount("/static", StaticFiles(directory="static"), name="static")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama3-8b-8192"
ALLOWED_MODELS = {
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
}


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", encoding="utf-8") as f:
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

    async def stream():
        if not GROQ_API_KEY:
            yield "[Server error] GROQ_API_KEY is missing. Add it to your .env or environment."
            return

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST",
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                },
            ) as resp:
                if resp.status_code >= 400:
                    details = await resp.aread()
                    yield f"[Provider error {resp.status_code}] {details.decode(errors='ignore')}"
                    return

                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            token = chunk["choices"][0]["delta"].get("content", "")
                            if token:
                                yield token
                        except Exception:
                            continue

    return StreamingResponse(stream(), media_type="text/plain")
