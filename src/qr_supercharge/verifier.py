"""QR code verification using pyzbar."""

from PIL import Image
from pyzbar.pyzbar import decode
from pyzbar.wrapper import ZBarSymbol


def verify_qr_code(image: Image.Image, expected_url: str) -> bool:
    """
    Verify that a QR code image decodes to the expected URL.

    Args:
        image: PIL Image of the QR code
        expected_url: The URL that should be decoded

    Returns:
        True if QR code is valid and matches expected URL
    """
    try:
        # Decode the QR code
        results = decode(image, symbols=[ZBarSymbol.QRCODE])

        if not results:
            return False

        # Check if any decoded result matches the expected URL
        for result in results:
            decoded_url = result.data.decode("utf-8")
            if decoded_url == expected_url:
                return True

        return False
    except Exception:
        return False


def decode_qr_code(image: Image.Image) -> list[str]:
    """
    Decode a QR code image and return all detected URLs.

    Args:
        image: PIL Image of the QR code

    Returns:
        List of decoded strings
    """
    try:
        results = decode(image, symbols=[ZBarSymbol.QRCODE])
        return [result.data.decode("utf-8") for result in results]
    except Exception:
        return []
