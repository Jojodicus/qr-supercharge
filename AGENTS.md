# Agent Guidelines for QR Supercharge

## Build & Development Commands

```bash
# Setup (run once)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run all tests
pytest src/tests/ -v

# Run a single test
pytest src/tests/test_qr_supercharge.py::test_font_data -v

# Run tests matching a pattern
pytest -k "test_qr" -v

# Format code
black src/

# Lint code
ruff check src/
ruff format src/

# Run the CLI tool
qr-embed "https://example.com" -v

# Run web API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Docker commands
docker-compose up --build
docker-compose down
```

## Code Style Guidelines

### Python Version & Types
- Target Python 3.10+
- Use `list[Type]` instead of `List[Type]` (PEP 585)
- Use `Type1 | Type2` instead of `Optional` or `Union`
- Use `| None` for optional parameters

### Imports (Order Matters)
```python
"""Module docstring."""

# 1. Standard library imports
import os
from typing import Set, Tuple
from urllib.parse import urlparse

# 2. Third-party imports
import click
from PIL import Image
import qrcode
import qrcode.constants

# 3. Local imports (mix of relative and absolute)
from . import qr_generator
from . import verifier
from qr_supercharge import font_data, placement
```

### Naming Conventions
- **Functions**: `snake_case` - `get_finder_pattern_positions()`
- **Variables**: `snake_case` - `text_width`, `center_row`
- **Constants**: `UPPER_CASE` - `CHAR_WIDTH`, `FONT_3X5`
- **Type hints**: Use descriptive names - `qr_matrix: list[list[bool]]`

### Code Formatting
- Line length: Follow black defaults (88 chars)
- Use double quotes for strings
- Trailing commas in multi-line collections
- Two blank lines between top-level functions/classes
- One blank line between methods

### Error Handling
```python
# Specific exceptions first, generic fallback last
try:
    result = some_operation()
except ValueError as e:
    # Handle specific error
    raise ValueError(f"Invalid input: {e}")
except RuntimeError as e:
    # Handle runtime errors
    return None
except Exception as e:
    # Fallback for unexpected errors
    click.echo(f"Unexpected error: {e}", err=True)
    return 1
```

### Documentation Style
```python
def function_name(param: type) -> return_type:
    """Short description.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass
```

## Project Structure

```
src/
├── qr_supercharge/     # Core QR generation library
│   ├── __init__.py
│   ├── cli.py         # CLI entry point (qr-embed command)
│   ├── font_data.py   # 3x5 pixel font definitions
│   ├── placement.py   # Safe zone calculations
│   ├── qr_generator.py # QR generation logic
│   └── verifier.py    # QR verification (pyzbar)
├── api/               # FastAPI web application
│   ├── __init__.py
│   └── main.py
└── tests/             # Test suite
    ├── __init__.py
    └── test_qr_supercharge.py
```

## Testing Guidelines
- Test files named `test_*.py`
- Test functions named `test_*`
- Use pytest fixtures where appropriate
- Use `click.testing.CliRunner` for CLI tests
- Use `tempfile.TemporaryDirectory()` for file operations

## Key Dependencies
- `qrcode` - QR code generation
- `Pillow` - Image processing
- `pyzbar` - QR decoding/verification
- `click` - CLI framework
- `fastapi` - Web API framework
- `uvicorn` - ASGI server
- `pytest` - Testing framework

## Notes
- Uses `uv` for dependency management
- Package uses hatchling build backend
- CLI script entry point: `qr-embed`
- API runs on port 8000 by default
- No Cursor rules or Copilot instructions found
