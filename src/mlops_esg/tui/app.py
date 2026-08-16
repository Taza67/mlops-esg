from __future__ import annotations

import asyncio

import httpx
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label

from mlops_esg.config import Settings
from mlops_esg.models import JobStatus


class EsgTui(App):
    """Host-side client. Talks only to the HTTP API."""

    TITLE = "mlops-esg"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f5", "analyze", "Analyze"),
    ]

    CSS = """
    #input-panel {
        height: auto;
        border: round $accent;
        padding: 1 2;
        margin: 1 2 0 2;
    }

    #input-panel Input {
        width: 100%;
        margin-bottom: 1;
    }

    #actions {
        height: auto;
    }

    #result-panel {
        height: 1fr;
        border: round $primary;
        padding: 1 2;
        margin: 1 2;
    }

    .row {
        height: auto;
        margin-bottom: 1;
    }

    .key {
        width: 10;
        color: $text-muted;
    }

    .value {
        width: 1fr;
    }
    """

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self._base_url = base_url

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="input-panel"):
            yield Input(placeholder="Sentence to classify (Enter or Analyze)", id="text")
            with Horizontal(id="actions"):
                yield Button("Analyze", id="analyze", variant="primary")
        with Vertical(id="result-panel"):
            with Horizontal(classes="row"):
                yield Label("Job", classes="key")
                yield Label("—", id="job-id", classes="value")
            with Horizontal(classes="row"):
                yield Label("Status", classes="key")
                yield Label("idle", id="phase", classes="value")
            with Horizontal(classes="row"):
                yield Label("Output", classes="key")
                yield Label("—", id="detail", classes="value")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self._base_url
        self.query_one("#input-panel").border_title = "Compose"
        self.query_one("#result-panel").border_title = "Job"
        self.query_one("#text", Input).focus()

    @on(Button.Pressed, "#analyze")
    @on(Input.Submitted, "#text")
    def action_analyze(self) -> None:
        text = self.query_one("#text", Input).value.strip()
        if not text:
            self._show(phase="idle", detail="Enter a sentence.")
            return
        self.analyze_and_poll(text)

    def _show(self, *, job_id: str | None = None, phase: str, detail: str = "—") -> None:
        if job_id is not None:
            self.query_one("#job-id", Label).update(job_id)
        self.query_one("#phase", Label).update(phase)
        self.query_one("#detail", Label).update(detail)

    @work(exclusive=True)
    async def analyze_and_poll(self, text: str) -> None:
        analyze = self.query_one("#analyze", Button)
        analyze.disabled = True
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=30.0) as client:
                response = await client.post("/analyze", json={"text": text})
                response.raise_for_status()
                job_id = response.json()["id"]
                self._show(job_id=job_id, phase=JobStatus.PENDING, detail="Queued")
                await self._poll_until_terminal(client, job_id)
        except httpx.HTTPError as exc:
            self._show(phase="error", detail=str(exc))
        finally:
            analyze.disabled = False

    async def _poll_until_terminal(self, client: httpx.AsyncClient, job_id: str) -> None:
        while True:
            response = await client.get(f"/status/{job_id}")
            if response.status_code == 404:
                self._show(job_id=job_id, phase="error", detail="Unknown job")
                return
            if response.is_error:
                self._show(job_id=job_id, phase="error", detail=f"HTTP {response.status_code}")
                return

            payload = response.json()
            job_status = payload["status"]
            if job_status in {JobStatus.PENDING, JobStatus.RUNNING}:
                self._show(job_id=job_id, phase=job_status, detail="Waiting for worker")
            elif job_status == JobStatus.DONE:
                self._show(job_id=job_id, phase=job_status, detail=str(payload["result"] or "—"))
                return
            elif job_status == JobStatus.FAILED:
                self._show(job_id=job_id, phase=job_status, detail=str(payload["error"] or "—"))
                return

            await asyncio.sleep(1)


def run() -> None:
    EsgTui(Settings().api_base_url).run()
