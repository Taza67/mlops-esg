from __future__ import annotations

import logging

from redis import Redis
from rq import Queue

from mlops_esg.config import Settings
from mlops_esg.ingest.stream import DocumentStream
from mlops_esg.job_service import JobService
from mlops_esg.store import RedisJobStore

logger = logging.getLogger(__name__)


class StreamConsumer:
    def __init__(self, stream: DocumentStream, jobs: JobService, group: str, consumer: str) -> None:
        self._stream = stream
        self._jobs = jobs
        self._group = group
        self._consumer = consumer

    def run_forever(self) -> None:
        self._stream.ensure_group(self._group)
        while True:
            for message_id, fields in self._stream.read_group(self._group, self._consumer):
                text = (fields.get("text") or fields.get("title") or "").strip()
                if not text:
                    self._stream.ack(self._group, message_id)
                    continue
                job_id = self._jobs.submit(text)
                self._stream.ack(self._group, message_id)
                logger.info("enqueued %s from %s", job_id, fields.get("guid", message_id))


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = Settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    stream = DocumentStream(redis, settings.stream_key)
    jobs = JobService(
        RedisJobStore(redis),
        Queue(settings.queue_name, connection=redis),
    )
    StreamConsumer(stream, jobs, settings.stream_group, settings.stream_consumer).run_forever()
