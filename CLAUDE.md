# CLAUDE.md — Browserling Integration (bli)

## Project Overview

`bli` is a Python CLI tool for **security URL detonation** using the [Browserling Live API](https://www.browserling.com/api). It lets analysts submit suspicious URLs to be opened inside sandboxed, isolated Browserling browser sessions — without ever touching the analyst's own machine.

## Architecture

```
cli.py          ← Click-based CLI entry point
bli/
  client.py     ← Browserling API client (session token requests)
  session.py    ← Session lifecycle management and URL construction
```

## Key Concepts

**Session flow (two steps):**
1. **Server-side**: Request a one-time session token from Browserling (`GET /liveapi_v1_session`, authenticated with `Browserling-Api-Key` header)
2. **Client-side**: Use the token to construct/open a live browser session URL pointing to the target

**Authentication**: API key loaded from `BROWSERLING_API_KEY` env var (or `.env` file).

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `BROWSERLING_API_KEY` | Yes | Your Browserling Live API key |
| `BLI_DEFAULT_BROWSER` | No | Default browser (`chrome`, `firefox`, `ie`, `edge`). Default: `chrome` |
| `BLI_DEFAULT_OS` | No | Default OS (`windows`, `macos`, `linux`). Default: `windows` |
| `BLI_OPEN_IN_BROWSER` | No | Auto-open session URL locally (`true`/`false`). Default: `true` |

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your BROWSERLING_API_KEY
```

## Running

```bash
# Detonate a single URL
python cli.py detonate https://suspicious-url.example.com

# Detonate with specific browser/OS
python cli.py detonate https://example.com --browser firefox --os macos

# Detonate multiple URLs from a file (one per line)
python cli.py detonate-batch urls.txt

# Show session info without opening
python cli.py detonate https://example.com --no-open
```

## Testing

```bash
# Run with a known safe URL to verify your API key works
python cli.py detonate https://example.com
```

## Linting / Formatting

```bash
pip install ruff
ruff check .
ruff format .
```
