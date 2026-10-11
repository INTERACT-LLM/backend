"""Fake LLM for load tests. Run from backend/:  uv run python -m tests.fake_llm"""
import asyncio
import json
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

# one answer that fits both immediate and general feedback
FEEDBACK = json.dumps({
    "has_language_error": False, "corrected_text": "Hola", "english_error_explanation": "",
    "positive": ["Bien"], "improvements": ["Más"],
})


def chunk(text: str) -> str:
    return "data: " + json.dumps({
        "id": "x", "object": "chat.completion.chunk", "created": int(time.time()), "model": "fake",
        "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": None}],
    }) + "\n\n"


async def stream():
    for _ in range(30):              # 30 words, 0.05 s apart, like a fast model
        await asyncio.sleep(0.05)
        yield chunk("hola ")
    yield "data: [DONE]\n\n"


@app.get("/v1/models")               # health check
async def models():
    return {"data": [{"id": "fake"}]}


@app.post("/v1/chat/completions")
async def completions(request: Request):
    body = await request.json()
    if body.get("stream"):           # chat answer
        return StreamingResponse(stream(), media_type="text/event-stream")
    await asyncio.sleep(1)           # feedback
    return {
        "id": "x", "object": "chat.completion", "created": int(time.time()), "model": "fake",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": FEEDBACK}, "finish_reason": "stop"}],
    }


if __name__ == "__main__":
    uvicorn.run(app, port=9000, log_level="warning")