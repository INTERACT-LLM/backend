"""
Init FastAPI
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.lesson import router as lesson_router
from app.api.feedback import router as feedback_router
from app.api.session import router as session_router
from app.api.llm import router as llm_router
from app.services.health_monitor import monitor_primary_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch the background primary-health monitor.
    health_task = asyncio.create_task(monitor_primary_health())
    try:
        yield
    finally:
        # Shutdown: cancel and await the monitor cleanly.
        health_task.cancel()
        try:
            await health_task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # middleware - adjust origins as needed for production
    origins = ["http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # add default root endpoint for health checks
    @app.get("/")
    def root():
        return {"status": "ok"}

    # add chat router (more routers added later)
    prefix = "/api"
    app.include_router(session_router, prefix=prefix)
    app.include_router(llm_router, prefix=prefix)
    app.include_router(chat_router, prefix=prefix)
    app.include_router(lesson_router, prefix=prefix)
    app.include_router(feedback_router, prefix=prefix)

    return app


# launch api
app = create_app()