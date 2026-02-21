# CLAUDE.md — Browserling Integration (bli)

## Project Overview

`bli` is a Python CLI for **security URL detonation** using the
[Browserling Live API](https://www.browserling.com/api). It opens suspicious
URLs inside isolated, sandboxed browser sessions — safely away from the
analyst's own machine.

## Architecture

```
cli.py              ← Click-based CLI (detonate / detonate-batch)
bli/
  config.py         ← Pydantic BaseSettings (loads from env / .env)
  client.py         ← Browserling API client (sync + async token requests)
  session.py        ← Detonation lifecycle; async batch via asyncio.gather
```

## Key Concepts

**Session flow (two steps):**
1. **Server-side**: `GET /liveapi_v1_session` with `Browserling-Api-Key` header
   → one-time `SessionToken` (Pydantic model)
2. **Client-side**: use `session_url` to open the sandboxed browser

**Batch concurrency**: `detonate-batch` fires all token requests in parallel
via `asyncio.gather` + a shared `httpx.AsyncClient`, then opens the sessions
sequentially (if `--no-open` is not set).

**Pydantic models**:
- `BrowserlingConfig` (BaseSettings) — env-driven config, `SecretStr` for key
- `SessionToken` — validated API response
- `DetonationResult` — per-URL outcome, serialisable to JSON

## Environment Variables

All prefixed with `BROWSERLING_` (loaded automatically by `BrowserlingConfig`):

| Variable | Required | Default | Description |
|---|---|---|---|
| `BROWSERLING_API_KEY` | Yes | — | Browserling Live API key |
| `BROWSERLING_DEFAULT_BROWSER` | No | `chrome` | Default browser |
| `BROWSERLING_DEFAULT_OS` | No | `windows` | Default OS |
| `BROWSERLING_TIMEOUT` | No | `15.0` | HTTP timeout in seconds |

## Development Setup

```bash
# Install uv if needed
curl -Ls https://astral.sh/uv/install.sh | sh

# Create venv and install deps
uv venv
uv pip install -e .

cp .env.example .env
# Edit .env — set BROWSERLING_API_KEY
```

## Running

```bash
# Detonate a single URL
uv run bli detonate https://suspicious-url.example.com

# Detonate with a specific browser/OS
uv run bli detonate https://example.com --browser firefox --os macos

# Batch detonate (concurrent)
uv run bli detonate-batch urls.txt

# Batch — print session URLs only, don't open locally
uv run bli detonate-batch iocs.txt --no-open
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
```
