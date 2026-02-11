from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .core.config import settings
from .core.logging_setup import setup_logging
from .db.base import Base
from .db.session import engine
from .db import models as _models  # noqa: F401

setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Ghid admitere - API local",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def startup_init() -> None:
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)
