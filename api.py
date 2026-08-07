"""Entrypoint for uvicorn: `uvicorn api:app`."""

from mlops_esg.api.app import app

__all__ = ["app"]
