from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from redis import Redis
from rq import Queue

from mlops_esg.api.routes import router
from mlops_esg.config import Settings
from mlops_esg.job_service import JobService
from mlops_esg.store import RedisJobStore

_OPENAPI_TAGS = [
    {
        "name": "jobs",
        "description": "Submit classification jobs and poll their records.",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    store = RedisJobStore(redis)
    queue = Queue(settings.queue_name, connection=redis)
    app.state.settings = settings
    app.state.job_service = JobService(store, queue)
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="MLOps ESG",
        version="0.1.0",
        description=(
            "Enqueue a zero-shot classification job and poll its Redis record. "
            "The API never loads the Hugging Face model."
        ),
        openapi_tags=_OPENAPI_TAGS,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    application.include_router(router)
    return application


app = create_app()


def run() -> None:
    settings = Settings()
    uvicorn.run(
        "mlops_esg.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
    )
