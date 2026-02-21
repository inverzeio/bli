# bli — Browserling Integration

A Python CLI for **security URL detonation** via [Browserling](https://www.browserling.com). Submit suspicious URLs to be opened inside isolated, sandboxed browser sessions — safely away from your own machine.

## Quickstart

```bash
# Install uv if needed
curl -Ls https://astral.sh/uv/install.sh | sh

# Create venv and install
uv venv
uv pip install -e .

cp .env.example .env
# Add your BROWSERLING_API_KEY to .env

uv run bli detonate https://suspicious-url.example.com
```

## Commands

| Command | Description |
|---|---|
| `detonate <url>` | Open a URL in a Browserling sandboxed session |
| `detonate-batch <file>` | Detonate all URLs from a newline-delimited file (concurrent) |

## Options

| Flag | Default | Description |
|---|---|---|
| `--browser`, `-b` | `chrome` | `chrome`, `firefox`, `edge`, `ie` |
| `--browser-version`, `-V` | `latest` | Browser version (e.g. `11` for IE 11) |
| `--os` | `windows` | `windows`, `macos`, `linux` |
| `--os-version` | `10` | OS version |
| `--no-open` | — | Print session URL without opening locally |

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `BROWSERLING_API_KEY` | Yes | Your Browserling Live API key |
| `BROWSERLING_DEFAULT_BROWSER` | No | Default browser (default: `chrome`) |
| `BROWSERLING_DEFAULT_OS` | No | Default OS (default: `windows`) |
| `BROWSERLING_TIMEOUT` | No | HTTP timeout in seconds (default: `15.0`) |

## Examples

```bash
# Detonate a single URL
uv run bli detonate https://suspicious.example.com

# Use a specific browser and OS
uv run bli detonate https://example.com --browser firefox --os macos

# Batch detonate from a file (concurrent)
uv run bli detonate-batch urls.txt

# Batch — print session URLs only, don't open locally
uv run bli detonate-batch iocs.txt --no-open
```

## Requirements

- Python 3.9+
- [uv](https://github.com/astral-sh/uv)
- A [Browserling Live API](https://www.browserling.com/api) key
