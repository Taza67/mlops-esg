<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![Python][python-shield]][python-url]

<div align="center">

<h3 align="center">mlops-esg</h3>

  <p align="center">
    Asynchronous zero-shot ESG text classification: FastAPI job API, Redis Queue workers with BART-MNLI, a host Textual client, and optional RSS ingest into a Redis Stream.
    <br />
    <br />
    <a href="https://github.com/Taza67/mlops-esg/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/Taza67/mlops-esg/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

`mlops-esg` classifies short texts into **Environment**, **Social**, or **Governance** with Hugging Face `facebook/bart-large-mnli`. The HTTP API enqueues work and stores a job **hash** in Redis. An RQ worker loads the model and writes `pending` / `running` / `done` / `failed`. A Textual TUI on the host polls `GET /status/{id}` without blocking the UI.

A separate ingest path polls a public BBC RSS feed, appends items to a Redis **Stream** (`esg:documents`), and a consumer group submits the same classify jobs through `JobService`.

### Built With

* [Python](https://www.python.org/) 3.11+
* [FastAPI](https://fastapi.tiangolo.com/)
* [Redis](https://redis.io/) / [RQ](https://python-rq.org/)
* [Transformers](https://huggingface.co/docs/transformers) (`facebook/bart-large-mnli`)
* [Textual](https://textual.textualize.io/)
* [uv](https://docs.astral.sh/uv/)
* [Docker Compose](https://docs.docker.com/compose/)

<p align="right"><a href="#readme-top" title="Back to top">↑</a></p>

## Getting Started

### Prerequisites

* Python 3.11 or newer
* [uv](https://docs.astral.sh/uv/)
* Redis 7 listening on `localhost:6379` (host mode)
* Docker or Podman (optional Compose stack: Redis, API, worker)

The first worker job downloads BART from the Hugging Face Hub. Later runs reuse the local cache (`HF_HOME` in Compose).

### Installation

```bash
git clone https://github.com/Taza67/mlops-esg.git
cd mlops-esg
uv sync
```

<p align="right"><a href="#readme-top" title="Back to top">↑</a></p>

## Usage

### Host processes

Start Redis, then in separate terminals:

```bash
uv run rq worker --url redis://localhost:6379/0 default
uv run mlops-esg-api
uv run python tui.py
```

Open API docs at `http://127.0.0.1:8000/docs`.

Submit without the TUI:

```bash
curl -s -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"The firm cut carbon emissions and published a climate report."}'
curl -s http://127.0.0.1:8000/status/<id>
```

RSS ingest (once) then consume into RQ:

```bash
MLOPS_ESG_RSS_ONCE=true uv run python ingest.py
uv run python consume.py
```

Configuration uses the `MLOPS_ESG_` prefix (`REDIS_URL` is also set for RQ in Compose). Examples: `MLOPS_ESG_REDIS_URL`, `MLOPS_ESG_API_BASE_URL`, `MLOPS_ESG_RSS_FEED_URL`.

### Compose

API and worker in containers; TUI and ingest stay on the host (Redis is published on `6379`):

```bash
docker compose up --build
uv run python tui.py
```

<p align="right"><a href="#readme-top" title="Back to top">↑</a></p>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating.

<p align="right"><a href="#readme-top" title="Back to top">↑</a></p>

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

<p align="right"><a href="#readme-top" title="Back to top">↑</a></p>

## Contact

Taza67 - [tazaakil67@gmail.com](mailto:tazaakil67@gmail.com)

Project link : [https://github.com/Taza67/mlops-esg](https://github.com/Taza67/mlops-esg)

<p align="right"><a href="#readme-top" title="Back to top">↑</a></p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/Taza67/mlops-esg.svg
[contributors-url]: https://github.com/Taza67/mlops-esg/graphs/contributors
[issues-shield]: https://img.shields.io/github/issues/Taza67/mlops-esg.svg
[issues-url]: https://github.com/Taza67/mlops-esg/issues
[license-shield]: https://img.shields.io/badge/License-MIT-blue.svg
[license-url]: https://github.com/Taza67/mlops-esg/blob/main/LICENSE
[python-shield]: https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white
[python-url]: https://www.python.org/
