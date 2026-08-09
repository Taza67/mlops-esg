from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IngestDocument:
    guid: str
    title: str
    text: str
    link: str
