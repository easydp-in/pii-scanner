"""Verhoeff algorithm implementation for Aadhaar 12th check digit validation.

The Verhoeff algorithm is a dihedral error-detection code that detects all single-digit
errors and all transposition errors between adjacent digits.
"""

D_TABLE = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)

P_TABLE = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)

INV_TABLE = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def calculate_verhoeff(num: str) -> str:
    """Calculate the Verhoeff check digit for a string of digits."""
    if not num or not num.isdigit():
        raise ValueError("Input must be a non-empty numeric string")

    c = 0
    for i, char in enumerate(reversed(num)):
        c = D_TABLE[c][P_TABLE[(i + 1) % 8][int(char)]]
    return str(INV_TABLE[c])


def validate_verhoeff(num: str) -> bool:
    """Validate whether a string of digits passes the Verhoeff checksum."""
    if not num or not num.isdigit():
        return False

    c = 0
    for i, char in enumerate(reversed(num)):
        c = D_TABLE[c][P_TABLE[i % 8][int(char)]]
    return c == 0
