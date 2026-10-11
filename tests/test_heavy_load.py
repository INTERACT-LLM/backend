"""
30 learners at once against the running backend, then check nothing was lost.
Run from backend/:  APP_ENV=.env.rehearsal uv run python -m tests.load_test
"""
import asyncio
import time
import uuid

import httpx

from app.services.store_interactions.store_chat import get_chat
from app.services.store_interactions.store_feedback import get_feedback

LEARNERS, TURNS = 30, 5


async def learner(client: httpx.AsyncClient, i: int) -> bool:
    r = await client.post("/api/chat", json={"user_profile": {
        "name": f"loadtest{i}", "browser_id": uuid.uuid4().hex,
        "language": "Spanish", "proficiency_level": "intermediate",
    }})
    chat_id = r.json()["chat_id"]

    for t in range(TURNS):
        msg = {"id": f"msg-{uuid.uuid4()}", "role": "user", "content": f"hola {t}"}

        async def chat():
            async with client.stream("POST", "/api/chat/message",
                                     json={"chat_id": chat_id, "message": msg}) as resp:
                async for _ in resp.aiter_lines():
                    pass

        # chat answer and feedback in parallel, like the frontend
        await asyncio.gather(chat(), client.post("/api/feedback/immediate", json={
            "last_user_message": msg, "chat_id": chat_id, "message_id": msg["id"],
        }))

    await client.post(f"/api/chat/{chat_id}/end", json={"reason": "user_ended"})
    await client.post("/api/feedback/detailed", json={
        "chat_id": chat_id,
        "messages": [{"role": "user", "content": f"hola {t}"} for t in range(TURNS)],
    })

    state, feedback = get_chat(chat_id), get_feedback(chat_id)
    return (state.n_user_turns == TURNS
            and state.ended_reason == "user_ended"
            and len(feedback) == TURNS + 1)   # one per message + one general


async def main():
    start = time.perf_counter()
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=120) as client:
        results = await asyncio.gather(*(learner(client, i) for i in range(LEARNERS)),
                                       return_exceptions=True)
    ok = sum(r is True for r in results)
    print(f"{ok}/{LEARNERS} learners OK in {time.perf_counter() - start:.1f}s")
    for r in results:
        if isinstance(r, Exception):
            print("  error:", repr(r))


asyncio.run(main())