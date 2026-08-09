"""Entrypoint for RQ: `rq worker default` imports worker.classify_text."""

from mlops_esg.worker.tasks import classify_text

__all__ = ["classify_text"]
