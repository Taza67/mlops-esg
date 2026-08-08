from __future__ import annotations

from transformers import pipeline

from mlops_esg.config import Settings
from mlops_esg.models import EsgLabel


class ZeroShotEsgClassifier:
    """Loads BART-MNLI once per worker process, then scores candidate labels."""

    def __init__(self, model_id: str) -> None:
        self._model_id = model_id
        self._pipeline = None

    def classify(self, text: str) -> EsgLabel:
        scores = self._load()(
            text,
            candidate_labels=[label.value for label in EsgLabel],
        )
        return EsgLabel(scores["labels"][0])

    def _load(self):
        if self._pipeline is None:
            self._pipeline = pipeline(
                "zero-shot-classification",
                model=self._model_id,
            )
        return self._pipeline


def build_classifier(settings: Settings | None = None) -> ZeroShotEsgClassifier:
    resolved = settings or Settings()
    return ZeroShotEsgClassifier(resolved.model_id)
