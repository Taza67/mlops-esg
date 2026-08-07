"""RQ entrypoint. Model load and mark_done / mark_failed come in the worker step."""

from __future__ import annotations


def classify_text(job_id: str, text: str) -> None:
    raise NotImplementedError("worker step: zero-shot BART")
