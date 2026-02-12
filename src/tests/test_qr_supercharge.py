"""Test cases for QR Supercharge."""

import os
import tempfile
from PIL import Image
import pytest
from qr_supercharge import font_data, placement, qr_generator, verifier


def test_font_data():
    """Test font data loading."""
    char_a = font_data.get_char("A")
    assert len(char_a) == 5  # 5 rows
    assert len(char_a[0]) == 3  # 3 columns per row

    width = font_data.calculate_text_width("ABC")
    assert width == 3 * 3 + 2 * 1  # 3 chars * 3 width + 2 spaces * 1 spacing

    height = font_data.calculate_text_height()
    assert height == 5


def test_qr_generation():
    """Test basic QR generation."""
    url = "https://example.com"
    qr = qr_generator.create_qr_code(url, version=5)
    assert qr is not None
    assert qr.version == 5


def test_text_overlay():
    """Test text overlay on QR code."""
    url = "https://example.com"
    text = "TEST"

    img, qr, pos = qr_generator.generate_qr_with_text(url, text, version=9)
    assert img is not None
    assert pos is not None

    # Verify the QR still works
    assert verifier.verify_qr_code(img, url)


def test_verification():
    """Test QR code verification."""
    url = "https://example.com"
    qr = qr_generator.create_qr_code(url, version=5)
    img = qr.make_image().convert("RGB")

    assert verifier.verify_qr_code(img, url)
    assert not verifier.verify_qr_code(img, "https://wrong-url.com")


def test_placement_algorithm():
    """Test placement algorithm finds valid positions."""
    import qrcode

    url = "https://example.com"
    qr = qr_generator.create_qr_code(url, version=9)
    matrix = placement.get_qr_matrix(qr)

    # Try to place text that should fit
    text_width = font_data.calculate_text_width("TEST")
    text_height = font_data.calculate_text_height()

    pos = placement.find_best_text_placement(9, matrix, text_width, text_height)
    assert pos is not None


def test_cli_basic():
    """Test CLI basic functionality."""
    from click.testing import CliRunner
    from qr_supercharge.cli import main, extract_domain

    runner = CliRunner()

    # Test domain extraction
    assert extract_domain("https://github.com") == "GITHUB.COM"
    assert extract_domain("https://www.example.com") == "EXAMPLE.COM"

    # Test CLI with temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test.png")
        result = runner.invoke(main, ["https://example.com", "-o", output_path])
        assert result.exit_code == 0
        assert os.path.exists(output_path)
