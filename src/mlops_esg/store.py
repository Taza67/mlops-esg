from __future__ import annotations

from typing import Protocol

from redis import Redis

from mlops_esg.models import JobRecord, JobStatus

_KEY_PREFIX = "job:"
_FIELD_STATUS = "status"
_FIELD_RESULT = "result"
_FIELD_ERROR = "error"


class JobStore(Protocol):
    def create_pending(self, job_id: str) -> None: ...

    def get(self, job_id: str) -> JobRecord | None: ...

    def mark_running(self, job_id: str) -> None: ...

    def mark_done(self, job_id: str, result: str) -> None: ...

    def mark_failed(self, job_id: str, error: str) -> None: ...


class RedisJobStore:
    """Job record (hash). Distinct from the RQ list and from the document stream."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def create_pending(self, job_id: str) -> None:
        self._write(job_id, JobStatus.PENDING)

    def get(self, job_id: str) -> JobRecord | None:
        data = self._redis.hgetall(_key(job_id))
        if not data:
            return None
        return JobRecord(
            id=job_id,
            status=JobStatus(data[_FIELD_STATUS]),
            result=_empty_to_none(data.get(_FIELD_RESULT, "")),
            error=_empty_to_none(data.get(_FIELD_ERROR, "")),
        )

    def mark_running(self, job_id: str) -> None:
        self._write(job_id, JobStatus.RUNNING)

    def mark_done(self, job_id: str, result: str) -> None:
        self._write(job_id, JobStatus.DONE, result=result)

    def mark_failed(self, job_id: str, error: str) -> None:
        self._write(job_id, JobStatus.FAILED, error=error)

    def _write(
        self,
        job_id: str,
        status: JobStatus,
        *,
        result: str = "",
        error: str = "",
    ) -> None:
        self._redis.hset(
            _key(job_id),
            mapping={
                _FIELD_STATUS: status.value,
                _FIELD_RESULT: result,
                _FIELD_ERROR: error,
            },
        )


def _key(job_id: str) -> str:
    return f"{_KEY_PREFIX}{job_id}"


def _empty_to_none(value: str) -> str | None:
    return value or None
