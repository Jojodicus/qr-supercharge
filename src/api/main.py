"""FastAPI backend for QR Supercharge web application."""

import base64
import io
from urllib.parse import urlparse
from typing import Optional

import qrcode
import qrcode.constants
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

# We need to import from qr_supercharge - adjust path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from qr_supercharge import qr_generator
from qr_supercharge import verifier

app = FastAPI(
    title="QR Supercharge",
    description="Generate QR codes with embedded pixel-art text",
    version="0.1.0",
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    """Request model for QR generation."""

    url: HttpUrl
    text: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response model for QR generation."""

    success: bool
    qr_code: Optional[str] = None
    version: Optional[int] = None
    embedded_text: Optional[str] = None
    error: Optional[str] = None


def extract_domain(url: str) -> str:
    """Extract domain from URL for default text."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.upper()
    except Exception:
        return "QR-CODE"


def find_working_qr(
    url: str,
    text: str,
    start_version: int = 5,
    max_version: int = 40,
) -> tuple:
    """
    Find a QR version that works with the text overlay.

    Returns:
        Tuple of (image, final_version, iterations)
    """
    version = start_version
    iterations = 0

    while version <= max_version:
        iterations += 1

        try:
            # Try to generate QR with text
            img, qr, placement_pos = qr_generator.generate_qr_with_text(
                url, text, version, qrcode.constants.ERROR_CORRECT_H
            )

            # Verify the QR code
            if verifier.verify_qr_code(img, url):
                return img, version, iterations

        except ValueError:
            pass
        except Exception:
            pass

        # Increase version by 2 for next attempt
        version += 2

    raise RuntimeError(
        f"Could not generate scannable QR code after {iterations} iterations. "
        f"Maximum version {max_version} reached."
    )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_qr(request: GenerateRequest):
    """Generate a QR code with embedded text."""
    url = str(request.url)

    # Determine text to embed
    text = request.text
    if text is None or text.strip() == "":
        text = extract_domain(url)

    # Validate text length
    if len(text) < 1:
        return GenerateResponse(success=False, error="Text cannot be empty")

    if len(text) > 15:
        # Warn but still try
        pass

    try:
        # Generate QR code with text
        img, final_version, iterations = find_working_qr(url, text)

        # Convert PIL Image to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return GenerateResponse(
            success=True,
            qr_code=f"data:image/png;base64,{img_base64}",
            version=final_version,
            embedded_text=text,
        )

    except RuntimeError as e:
        return GenerateResponse(success=False, error=str(e))
    except Exception as e:
        return GenerateResponse(success=False, error=f"Unexpected error: {str(e)}")


# Serve static files from src/web/
# This will serve index.html at the root
static_path = os.path.join(os.path.dirname(__file__), "..", "web")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
