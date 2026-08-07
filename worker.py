"""RQ task alias: `rq worker default` can import worker.classify_text."""

from mlops_esg.worker.tasks import classify_text

__all__ = ["classify_text"]
 