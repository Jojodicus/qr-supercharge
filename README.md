# QR Supercharge

A Python CLI tool and web app that generates QR codes with pixel-art text embedded inside.

## Quick Start

### CLI

```bash
# Install
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Generate QR with auto-extracted domain
qr-embed "https://github.com"

# Custom text
qr-embed "https://example.com" --text "HELLO"
```

### Web App

```bash
# Run locally
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Or with Docker
docker-compose up --build
```

Access at http://localhost:8000

## Features

- **Smart Text Placement**: Avoids critical QR patterns (finder, timing, alignment)
- **Auto-Verification**: Every QR is decoded to ensure scannability
- **Auto-Scaling**: Increases QR version until text fits and works
- **3x5 Pixel Font**: Fits 10-15 characters in compact space
- **Web + CLI**: Use via browser or command line

## CLI Usage

```bash
qr-embed "https://github.com" \
  --text "GITHUB" \
  --output github.png \
  --verbose
```

**Options:**
- `URL`: Web address to encode (required)
- `-t, --text TEXT`: Text to embed (defaults to domain)
- `-o, --output PATH`: Output file path
- `-v, --verbose`: Show iteration details
- `-s, --start-version`: Starting QR version (default: 5)
- `-m, --max-version`: Maximum QR version (default: 40)

## API

`POST /api/generate`

```json
{
  "url": "https://github.com",
  "text": "GITHUB"
}
```

Response:
```json
{
  "success": true,
  "qr_code": "data:image/png;base64,...",
  "version": 9,
  "embedded_text": "GITHUB.COM"
}
```

## Project Structure

```
qr-supercharge/
├── src/
│   ├── qr_supercharge/    # Core QR generation
│   ├── api/               # FastAPI backend
│   └── web/               # Frontend (HTML/CSS/JS)
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Development

```bash
# Tests
pytest src/tests/ -v

# Format
black src/
ruff check src/

# Docker build
docker-compose up --build
```

## License

MIT
