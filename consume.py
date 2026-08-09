"""Entrypoint for the stream consumer: `python consume.py`."""

from mlops_esg.ingest.consumer import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
