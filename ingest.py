"""Entrypoint for the RSS producer: `python ingest.py`."""

from mlops_esg.ingest.rss import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
