from __future__ import annotations

import logging
import re
import time
import xml.etree.ElementTree as ET

import httpx
from redis import Redis

from mlops_esg.config import Settings
from mlops_esg.ingest.models import IngestDocument
from mlops_esg.ingest.stream import DocumentStream

logger = logging.getLogger(__name__)

_TAG = re.compile(r"<[^>]+>")


class RssProducer:
    def __init__(self, stream: DocumentStream, feed_url: str) -> None:
        self._stream = stream
        self._feed_url = feed_url

    def poll_once(self) -> int:
        xml = httpx.get(self._feed_url, timeout=30.0, follow_redirects=True)
        xml.raise_for_status()
        published = 0
        for document in _parse_rss(xml.text):
            if self._stream.try_publish(document):
                published += 1
                logger.info("published %s", document.guid)
        return published

    def run_forever(self, *, poll_seconds: int, once: bool) -> None:
        while True:
            count = self.poll_once()
            logger.info("poll done published=%s", count)
            if once:
                return
            time.sleep(poll_seconds)


def _parse_rss(body: str) -> list[IngestDocument]:
    root = ET.fromstring(body)
    documents: list[IngestDocument] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link or title).strip()
        raw = item.findtext("description") or title
        text = " ".join(_TAG.sub(" ", raw).split())
        if not guid or not text:
            continue
        documents.append(IngestDocument(guid=guid, title=title, text=text, link=link))
    return documents


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = Settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    producer = RssProducer(
        DocumentStream(redis, settings.stream_key),
        settings.rss_feed_url,
    )
    producer.run_forever(poll_seconds=settings.rss_poll_seconds, once=settings.rss_once)
