"""Unit tests for the Verhoeff checksum algorithm used in Aadhaar validation."""

import pytest

from pii_scanner.validators.verhoeff import calculate_verhoeff, validate_verhoeff


def test_calculate_verhoeff_valid_inputs() -> None:
    """Verifies that calculate_verhoeff returns the expected check digit."""
    # Example known values:
    # 236 -> 2363
    assert calculate_verhoeff("236") == "3"
    # 12345 -> 123451
    assert calculate_verhoeff("12345") == "1"


def test_validate_verhoeff_valid_numbers() -> None:
    """Verifies that validate_verhoeff validates numbers with correct check digits."""
    assert validate_verhoeff("2363") is True
    assert validate_verhoeff("123451") is True


def test_validate_verhoeff_invalid_numbers() -> None:
    """Verifies that corrupted check digits or single-digit errors fail validation."""
    assert validate_verhoeff("2364") is False
    assert validate_verhoeff("123452") is False


def test_validate_verhoeff_transposition_error() -> None:
    """Verifies that transposed adjacent digits are detected."""
    # 2363 -> transpose 2 and 3 -> 3263
    assert validate_verhoeff("3263") is False


def test_verhoeff_non_numeric_input() -> None:
    """Non-numeric input should fail validation gracefully."""
    assert validate_verhoeff("1234A51") is False
    assert validate_verhoeff("") is False
    with pytest.raises(ValueError):
        calculate_verhoeff("123A")
