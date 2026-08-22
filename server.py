from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv
import httpx
import os
import json
import uvicorn

load_dotenv()

app = FastAPI(title="NexusAI — ChatGPT Clone")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ── Current Groq Models (as of Aug 2026) ──────────────
# Old llama models are deprecated; updated to production + preview models
DEFAULT_MODEL = "openai/gpt-oss-120b"
ALLOWED_MODELS = {
    "openai/gpt-oss-120b",          # Flagship — 120B, reasoning, tools
    "openai/gpt-oss-20b",           # Fast — 20B, great latency
    "groq/compound",                # Agentic system — web search + code exec
    "groq/compound-mini",           # Lightweight agentic
    "qwen/qwen3.6-27b",             # Preview — reasoning, 27B
}

# Max completion tokens per model (to avoid exceeding limits)
MAX_TOKENS = {
    "openai/gpt-oss-120b": 65536,
    "openai/gpt-oss-20b": 65536,
    "groq/compound": 8192,
    "groq/compound-mini": 8192,
    "qwen/qwen3.6-27b": 16384,
}


@app.get("/api/models")
async def get_models():
    """Return available models for the frontend."""
    return {
        "default": DEFAULT_MODEL,
        "models": [
            {"id": "openai/gpt-oss-120b", "label": "GPT-OSS 120B · Flagship", "speed": "~500 t/s"},
            {"id": "openai/gpt-oss-20b", "label": "GPT-OSS 20B · Fast", "speed": "~1000 t/s"},
            {"id": "groq/compound", "label": "Compound · Agentic", "speed": "~450 t/s"},
            {"id": "groq/compound-mini", "label": "Compound Mini · Light", "speed": "~450 t/s"},
            {"id": "qwen/qwen3.6-27b", "label": "Qwen 3.6 27B · Reasoning", "speed": "~500 t/s"},
        ],
    }


@app.get("/", response_class=HTMLResponse)
async def home():
    path = os.path.join(os.path.dirname(__file__), "static/index.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
async def chat(request: Request):
    """Stream chat completions from Groq with real SSE streaming."""
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", DEFAULT_MODEL)

    if not isinstance(messages, list):
        messages = []
    if model not in ALLOWED_MODELS:
        model = DEFAULT_MODEL

    if not GROQ_API_KEY:
        return StreamingResponse(
            iter(["data: [DONE]\n\n"]),
            media_type="text/event-stream",
        )

    max_tokens = MAX_TOKENS.get(model, 8192)

    async def stream_groq():
        try:
            async with httpx.AsyncClient(timeout=120) as client:
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
                        "max_tokens": max_tokens,
                        "temperature": 0.7,
                    },
                ) as resp:
                    if resp.status_code >= 400:
                        error_text = await resp.aread()
                        error_msg = error_text.decode("utf-8", errors="replace")
                        error_data = json.dumps({
                            "error": True,
                            "status": resp.status_code,
                            "message": error_msg,
                        })
                        yield f"data: {error_data}\n\n"
                        yield "data: [DONE]\n\n"
                        return

                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                yield "data: [DONE]\n\n"
                                return
                            yield f"data: {data}\n\n"
        except httpx.ConnectError:
            error_data = json.dumps({
                "error": True,
                "message": "Could not connect to Groq API. Check your network or API key.",
            })
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = json.dumps({
                "error": True,
                "message": f"Unexpected error: {str(e)}",
            })
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_groq(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
