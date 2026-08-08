from __future__ import annotations

from redis import Redis

from mlops_esg.config import Settings
from mlops_esg.store import RedisJobStore
from mlops_esg.worker.classifier import build_classifier

_settings = Settings()
_store = RedisJobStore(Redis.from_url(_settings.redis_url, decode_responses=True))
_classifier = build_classifier(_settings)


def classify_text(job_id: str, text: str) -> None:
    _store.mark_running(job_id)
    try:
        label = _classifier.classify(text)
    except Exception as exc:
        _store.mark_failed(job_id, str(exc))
        raise
    _store.mark_done(job_id, label.value)
