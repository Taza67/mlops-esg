"""Entrypoint for the host TUI: `python tui.py`."""

from mlops_esg.tui.app import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
