from __future__ import annotations

from redis import Redis
from redis.exceptions import ResponseError

from mlops_esg.ingest.models import IngestDocument

_SEEN_SUFFIX = ":seen"
_MAXLEN = 2000


class DocumentStream:
    """Document inbox (stream). Distinct from the RQ list and from job hashes."""

    def __init__(self, redis: Redis, key: str) -> None:
        self._redis = redis
        self._key = key
        self._seen_key = f"{key}{_SEEN_SUFFIX}"

    def try_publish(self, document: IngestDocument) -> bool:
        if not self._redis.sadd(self._seen_key, document.guid):
            return False
        self._redis.xadd(
            self._key,
            {
                "guid": document.guid,
                "title": document.title,
                "text": document.text,
                "link": document.link,
            },
            maxlen=_MAXLEN,
            approximate=True,
        )
        return True

    def ensure_group(self, group: str) -> None:
        try:
            # id=0: backlog already in the stream is still readable with ">".
            self._redis.xgroup_create(self._key, group, id="0", mkstream=True)
        except ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    def read_group(
        self,
        group: str,
        consumer: str,
        *,
        count: int = 10,
        block_ms: int = 5000,
    ) -> list[tuple[str, dict[str, str]]]:
        pending = _entries(
            self._redis.xreadgroup(group, consumer, {self._key: "0"}, count=count)
        )
        if pending:
            return pending
        return _entries(
            self._redis.xreadgroup(
                group,
                consumer,
                {self._key: ">"},
                count=count,
                block=block_ms,
            )
        )

    def ack(self, group: str, message_id: str) -> None:
        self._redis.xack(self._key, group, message_id)


def _entries(rows: object) -> list[tuple[str, dict[str, str]]]:
    if not rows:
        return []
    messages: list[tuple[str, dict[str, str]]] = []
    for _stream, entries in rows:
        for message_id, fields in entries:
            messages.append((message_id, fields))
    return messages
