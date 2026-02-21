# bli — Browserling Integration

A Python CLI for **security URL detonation** via [Browserling](https://www.browserling.com). Submit suspicious URLs to be opened inside isolated, sandboxed browser sessions — safely away from your own machine.

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your BROWSERLING_API_KEY to .env

python cli.py detonate https://suspicious-url.example.com
```

## Commands

| Command | Description |
|---|---|
| `detonate <url>` | Open a URL in a Browserling sandboxed session |
| `detonate-batch <file>` | Detonate all URLs from a newline-delimited file |

## Options

| Flag | Description |
|---|---|
| `--browser` | `chrome` (default), `firefox`, `edge`, `ie` |
| `--os` | `windows` (default), `macos`, `linux` |
| `--no-open` | Print session URL without opening locally |
| `--version` | e.g. `11` for IE 11, `latest` for others |

## Requirements

- Python 3.9+
- A [Browserling Live API](https://www.browserling.com/api) key
