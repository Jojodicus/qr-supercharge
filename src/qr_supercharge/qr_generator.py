"""QR generation and text overlay functionality."""

from PIL import Image
import qrcode
import qrcode.constants
from . import font_data
from . import placement


def create_qr_code(
    url: str, version: int = 5, error_correction=qrcode.constants.ERROR_CORRECT_H
) -> qrcode.QRCode:
    """Create a QR code with specified parameters."""
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr


def overlay_text_on_qr(
    qr: qrcode.QRCode,
    text: str,
    placement_row: int,
    placement_col: int,
) -> Image.Image:
    """
    Overlay text onto a QR code with white background border.

    Args:
        qr: QR code object
        text: Text to overlay
        placement_row: Row to start placing text
        placement_col: Column to start placing text

    Returns:
        PIL Image with text overlaid
    """
    # Create the base QR image
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    pixels = img.load()

    # Get module size
    module_size = 10  # From box_size parameter

    # Calculate text dimensions in modules
    text_width = font_data.calculate_text_width(text)
    text_height = font_data.calculate_text_height()

    # Draw white background with 1 module padding on all sides
    padding = 1
    bg_start_row = (placement_row - padding) * module_size
    bg_start_col = (placement_col - padding) * module_size
    bg_height = (text_height + 2 * padding) * module_size
    bg_width = (text_width + 2 * padding) * module_size

    for r in range(bg_height):
        for c in range(bg_width):
            pixels[bg_start_col + c, bg_start_row + r] = (255, 255, 255)

    # Overlay each character in black
    current_col = placement_col
    for char in text.upper():
        char_pixels = font_data.get_char(char)

        # Draw the character
        for row_idx, row in enumerate(char_pixels):
            for col_idx, pixel in enumerate(row):
                if pixel == 1:
                    # Calculate pixel position
                    pixel_row = (placement_row + row_idx) * module_size
                    pixel_col = (current_col + col_idx) * module_size

                    # Fill the module with black (make it dark)
                    for pr in range(module_size):
                        for pc in range(module_size):
                            pixels[pixel_col + pc, pixel_row + pr] = (0, 0, 0)

        current_col += font_data.CHAR_WIDTH + font_data.CHAR_SPACING

    return img


def generate_qr_with_text(
    url: str,
    text: str,
    version: int = 5,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
) -> tuple[Image.Image, qrcode.QRCode, tuple[int, int]]:
    """
    Generate a QR code with embedded text.

    Returns:
        Tuple of (image, qr_code, placement_position)
    """
    # Create QR code
    qr = create_qr_code(url, version, error_correction)

    # Get QR matrix
    qr_matrix = placement.get_qr_matrix(qr)

    # Calculate text dimensions
    text_width = font_data.calculate_text_width(text)
    text_height = font_data.calculate_text_height()

    # Find best placement
    placement_pos = placement.find_best_text_placement(
        version, qr_matrix, text_width, text_height
    )

    if placement_pos is None:
        raise ValueError(f"Cannot fit text '{text}' in QR version {version}")

    # Overlay text
    img = overlay_text_on_qr(qr, text, placement_pos[0], placement_pos[1])

    return img, qr, placement_pos
