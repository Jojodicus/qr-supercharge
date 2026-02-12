"""Safe zone calculations for QR text placement."""

from typing import Set, Tuple
import qrcode
import qrcode.util


def get_finder_pattern_positions(version: int) -> Set[Tuple[int, int]]:
    """Get all positions covered by finder patterns (3 corners, 8x8 each with separator)."""
    positions = set()
    size = 17 + 4 * version

    # Top-left corner (including separator) - finder pattern is 7x7 at 0,0 with 1 module separator
    for row in range(9):
        for col in range(9):
            positions.add((row, col))

    # Top-right corner - finder pattern at 0, size-7 with separator
    for row in range(9):
        for col in range(size - 8, size):
            positions.add((row, col))

    # Bottom-left corner - finder pattern at size-7, 0 with separator
    for row in range(size - 8, size):
        for col in range(9):
            positions.add((row, col))

    return positions


def get_timing_pattern_positions(version: int) -> Set[Tuple[int, int]]:
    """Get positions covered by timing patterns (row 6 and column 6, 0-indexed)."""
    positions = set()
    size = 17 + 4 * version

    # Row 6 (horizontal timing pattern) - skip finder pattern areas
    for col in range(8, size - 8):
        positions.add((6, col))

    # Column 6 (vertical timing pattern) - skip finder pattern areas
    for row in range(8, size - 8):
        positions.add((row, 6))

    return positions


def get_alignment_pattern_positions(version: int) -> Set[Tuple[int, int]]:
    """Get positions covered by alignment patterns (version >= 2)."""
    positions = set()

    if version < 2:
        return positions

    # Get alignment pattern centers for this version
    centers = qrcode.util.pattern_position(version)

    # Each alignment pattern is 5x5
    for center_row in centers:
        for center_col in centers:
            # Skip if this is where a finder pattern is
            if (
                (center_row <= 8 and center_col <= 8)
                or (center_row <= 8 and center_col >= 17 + 4 * version - 8)
                or (center_row >= 17 + 4 * version - 8 and center_col <= 8)
            ):
                continue

            for row in range(center_row - 2, center_row + 3):
                for col in range(center_col - 2, center_col + 3):
                    if 0 <= row < 17 + 4 * version and 0 <= col < 17 + 4 * version:
                        positions.add((row, col))

    return positions


def get_dark_module_position(version: int) -> Tuple[int, int]:
    """Get position of the dark module (always at specific location)."""
    return (4 * version + 9, 8)


def get_forbidden_positions(version: int) -> Set[Tuple[int, int]]:
    """Get all positions that should not be modified (within QR matrix only)."""
    forbidden = set()
    forbidden.update(get_finder_pattern_positions(version))
    forbidden.update(get_timing_pattern_positions(version))
    forbidden.update(get_alignment_pattern_positions(version))
    # Don't include quiet zone - it's outside the QR matrix
    return forbidden


def get_qr_matrix(qr: qrcode.QRCode) -> list[list[bool]]:
    """Convert QR code to a 2D boolean matrix."""
    return [
        [bool(cell) if cell is not None else False for cell in row]
        for row in qr.modules
    ]


def find_largest_safe_rectangle(
    safe_grid: list[list[bool]], min_width: int, min_height: int
) -> Tuple[int, int, int, int] | None:
    """
    Find the largest rectangular safe zone using dynamic programming approach.
    Returns (row, col, width, height) or None.
    """
    if not safe_grid or not safe_grid[0]:
        return None

    rows = len(safe_grid)
    cols = len(safe_grid[0])

    # dp[i][j] = height of consecutive safe cells ending at (i, j)
    dp = [[0] * cols for _ in range(rows)]

    best_area = 0
    best_rect = None

    for i in range(rows):
        for j in range(cols):
            if safe_grid[i][j]:
                if i == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = dp[i - 1][j] + 1

                # Try to extend to the left to form a rectangle
                min_height_so_far = dp[i][j]
                for k in range(j, -1, -1):
                    if dp[i][k] == 0:
                        break
                    min_height_so_far = min(min_height_so_far, dp[i][k])
                    width = j - k + 1
                    height = min_height_so_far
                    area = width * height

                    if area > best_area and width >= min_width and height >= min_height:
                        best_area = area
                        best_rect = (i - height + 1, k, width, height)

    return best_rect


def find_best_text_placement(
    version: int, qr_matrix: list[list[bool]], text_width: int, text_height: int
) -> Tuple[int, int] | None:
    """
    Find the best position to place text.
    Returns (row, col) or None if no suitable position found.
    """
    forbidden = get_forbidden_positions(version)
    size = len(qr_matrix)

    # Create a grid of safe positions (True = safe to modify)
    safe_grid = []
    for row in range(size):
        safe_row = []
        for col in range(size):
            is_safe = (row, col) not in forbidden
            safe_row.append(is_safe)
        safe_grid.append(safe_row)

    # Find the largest safe rectangle
    rect = find_largest_safe_rectangle(safe_grid, text_width, text_height)

    if rect is None:
        return None

    row, col, width, height = rect

    # Center the text within this rectangle
    center_row = row + (height - text_height) // 2
    center_col = col + (width - text_width) // 2

    return (center_row, center_col)
