from __future__ import annotations

import uuid

from rq import Queue

from mlops_esg.models import JobRecord
from mlops_esg.store import JobStore

CLASSIFY_TASK = "mlops_esg.worker.tasks.classify_text"


class JobService:
    def __init__(self, store: JobStore, queue: Queue) -> None:
        self._store = store
        self._queue = queue

    def submit(self, text: str) -> str:
        job_id = str(uuid.uuid4())
        self._store.create_pending(job_id)
        self._queue.enqueue(CLASSIFY_TASK, job_id, text, job_id=job_id)
        return job_id

    def get(self, job_id: str) -> JobRecord | None:
        return self._store.get(job_id)
