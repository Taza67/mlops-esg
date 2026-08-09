# Contributing

Thank you for your interest in **mlops-esg**. The project is an asynchronous zero-shot ESG classifier: FastAPI, Redis (job hashes, RQ, document stream), a Hugging Face worker, a host Textual client, and RSS ingest.

## Before you start

- Search the [existing issues](https://github.com/Taza67/mlops-esg/issues) to avoid duplicating work.
- For large or structural changes, open an issue first.

## Development environment

### Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Redis 7 on `localhost:6379` for host processes

### Clone and install

```bash
git clone https://github.com/Taza67/mlops-esg.git
cd mlops-esg
uv sync
```

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Make focused changes; keep the PRs easy to review.
3. Make sure `uv sync` succeeds and the processes you touch still start (`mlops-esg-api`, `rq worker`, TUI, ingest).
4. Open a pull request with a clear description and link the related issues.

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/).

- **Types:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- **Description:** imperative, lowercase, no trailing period
- **Body:** optional; blank line after the description, then `-` bullets — lowercase except proper nouns, imperative, no trailing period

## Code organization

| Path | Role |
|------|------|
| `src/mlops_esg/api/` | FastAPI app, OpenAPI routes and wire schemas |
| `src/mlops_esg/job_service.py` | Create job hash then enqueue RQ |
| `src/mlops_esg/store.py` | Job record hash in Redis |
| `src/mlops_esg/worker/` | RQ task and BART-MNLI classifier |
| `src/mlops_esg/tui/` | Host Textual client (HTTP only) |
| `src/mlops_esg/ingest/` | RSS producer, document stream, consumer group |
| `src/mlops_esg/config.py` | Settings (`MLOPS_ESG_` prefix) |
| `api.py` / `worker.py` / `tui.py` / `ingest.py` / `consume.py` | Process entry shims |
| `docker-compose.yml` | Redis, API, and RQ worker |

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to abide by it.
