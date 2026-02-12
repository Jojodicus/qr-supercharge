"""Command-line interface for QR Supercharge."""

import os
import click
from urllib.parse import urlparse
import qrcode
import qrcode.constants
from . import qr_generator
from . import verifier


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
    verbose: bool = False,
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

        if verbose:
            click.echo(f"Attempt {iterations}: Trying QR version {version}...")

        try:
            # Try to generate QR with text
            img, qr, placement_pos = qr_generator.generate_qr_with_text(
                url, text, version, qrcode.constants.ERROR_CORRECT_H
            )

            if verbose:
                click.echo(f"  Generated QR code, verifying...")

            # Verify the QR code
            if verifier.verify_qr_code(img, url):
                if verbose:
                    click.echo(f"  Success! QR code is scannable.")
                return img, version, iterations
            else:
                if verbose:
                    click.echo(f"  QR code not scannable, increasing version...")
        except ValueError as e:
            if verbose:
                click.echo(f"  {e}")
        except Exception as e:
            if verbose:
                click.echo(f"  Error: {e}")

        # Increase version by 2 for next attempt
        version += 2

    raise RuntimeError(
        f"Could not generate scannable QR code after {iterations} iterations. "
        f"Maximum version {max_version} reached."
    )


@click.command()
@click.argument("url")
@click.option("--text", "-t", help="Text to embed (defaults to domain from URL)")
@click.option("--output", "-o", help="Output file path")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.option(
    "--start-version", "-s", default=5, help="Starting QR version (default: 5)"
)
@click.option(
    "--max-version", "-m", default=40, help="Maximum QR version (default: 40)"
)
def main(
    url: str,
    text: str | None,
    output: str | None,
    verbose: bool,
    start_version: int,
    max_version: int,
):
    """Generate QR codes with embedded pixel-art text.

    URL is the web address to encode in the QR code.
    """
    # Determine text to embed
    if text is None:
        text = extract_domain(url)

    # Validate text length
    if len(text) < 1:
        click.echo("Error: Text cannot be empty", err=True)
        return 1

    if len(text) > 15:
        click.echo(
            f"Warning: Text is {len(text)} characters, may be too long (recommended: 10-15)",
            err=True,
        )

    # Determine output file
    if output is None:
        # Generate filename from URL domain
        domain = extract_domain(url).lower().replace(".", "_")
        output = f"{domain}.png"

    # Ensure output directory exists
    output_dir = os.path.dirname(output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Generate QR code with text
        if verbose:
            click.echo(f"Generating QR code for: {url}")
            click.echo(f"Embedding text: {text}")

        img, final_version, iterations = find_working_qr(
            url, text, start_version, max_version, verbose
        )

        # Save the image
        img.save(output)

        # Report success
        click.echo(f"Generated QR code: {output}")
        click.echo(f"  QR Version: {final_version}")
        click.echo(f"  Iterations: {iterations}")
        click.echo(f"  Embedded Text: {text}")

        return 0

    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        return 1
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        return 1


if __name__ == "__main__":
    main()
