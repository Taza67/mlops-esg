from __future__ import annotations

import asyncio

import httpx
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Input, Static

from mlops_esg.config import Settings
from mlops_esg.models import JobStatus


class EsgTui(App):
    """Host-side client. Talks only to the HTTP API."""

    CSS = """
    Input { width: 100%; }
    #status { margin-top: 1; }
    """

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self._base_url = base_url

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Text to classify", id="text")
        yield Button("Analyze", id="analyze", variant="primary")
        yield Static("Idle", id="status")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "analyze":
            return
        text = self.query_one("#text", Input).value.strip()
        if not text:
            self.query_one("#status", Static).update("Enter some text.")
            return
        self.analyze_and_poll(text)

    @work(exclusive=True)
    async def analyze_and_poll(self, text: str) -> None:
        status = self.query_one("#status", Static)
        async with httpx.AsyncClient(base_url=self._base_url, timeout=30.0) as client:
            response = await client.post("/analyze", json={"text": text})
            response.raise_for_status()
            job_id = response.json()["id"]
            status.update(f"pending  {job_id}")
            await self._poll_until_terminal(client, job_id)

    async def _poll_until_terminal(self, client: httpx.AsyncClient, job_id: str) -> None:
        status = self.query_one("#status", Static)
        while True:
            response = await client.get(f"/status/{job_id}")
            if response.status_code == 404:
                status.update(f"Unknown job {job_id}")
                return
            if response.is_error:
                status.update(f"HTTP {response.status_code} for job {job_id}")
                return

            payload = response.json()
            job_status = payload["status"]
            if job_status in {JobStatus.PENDING, JobStatus.RUNNING}:
                status.update(f"{job_status} {job_id}")
            elif job_status == JobStatus.DONE:
                status.update(f"done {job_id}: {payload['result']}")
                return
            elif job_status == JobStatus.FAILED:
                status.update(f"failed {job_id}: {payload['error']}")
                return

            await asyncio.sleep(1)


def run() -> None:
    EsgTui(Settings().api_base_url).run()
