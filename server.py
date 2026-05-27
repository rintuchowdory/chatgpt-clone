from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="ChatGPT Clone")

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
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
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    """Health check endpoint to verify API key configuration."""
    has_key = bool(os.getenv("GROQ_API_KEY", ""))
    return JSONResponse({
        "ok": True,
        "provider": "groq",
        "api_key_configured": has_key
    })


def sanitize_messages(raw_messages):
    """Validate and sanitize incoming chat messages."""
    if not isinstance(raw_messages, list):
        return []
    
    cleaned = []
    for item in raw_messages:
        if not isinstance(item, dict):
            continue
        
        role = item.get("role")
        content = item.get("content")
        
        # Validate role and content
        if role not in {"system", "user", "assistant"}:
            continue
        if not isinstance(content, str):
            continue
        
        content = content.strip()
        if not content:
            continue
        
        cleaned.append({"role": role, "content": content})
    
    # Keep only the last 40 messages to avoid token limits
    return cleaned[-40:]


@app.post("/chat")
async def chat(request: Request):
    """Stream chat responses from Groq API."""
    body = await request.json()
    messages = sanitize_messages(body.get("messages", []))
    model = body.get("model", DEFAULT_MODEL)
    
    if model not in ALLOWED_MODELS:
        model = DEFAULT_MODEL
    
    async def stream():
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            yield "[Server error] GROQ_API_KEY is missing. Add it to your environment or .env file."
            return

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST",
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "max_tokens": 1200,
                    "temperature": 0.6,
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
