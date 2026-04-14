"""
Init FastAPI
"""
from fastapi import FastAPI
from app.api.chat import router as chat_router

def create_app() -> FastAPI:
    app = FastAPI()

    # add chat router (more routers added later)
    app.include_router(chat_router)
    return app


# launch
app = create_app()
