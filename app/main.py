"""
Init FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI()

    origins = ["http://localhost:3000"]

    # add CORS 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # add chat router (more routers added later)
    app.include_router(chat_router)
    return app


# launch
app = create_app()
