"""Unit tests for Aadhaar number validation and safe redaction."""

from pii_scanner.validators.aadhaar import AadhaarValidator
from pii_scanner.validators.verhoeff import calculate_verhoeff


def generate_valid_aadhaar(prefix11: str) -> str:
    """Helper to generate a valid 12-digit Aadhaar given an 11-digit prefix starting with 2-9."""
    check_digit = calculate_verhoeff(prefix11)
    return prefix11 + check_digit


def test_aadhaar_validator_valid_numbers() -> None:
    validator = AadhaarValidator()
    # 3675 9834 256 + check digit
    valid_aadhaar = generate_valid_aadhaar("36759834256")
    assert validator.is_valid(valid_aadhaar) is True
    assert (
        validator.is_valid(f"{valid_aadhaar[:4]} {valid_aadhaar[4:8]} {valid_aadhaar[8:]}") is True
    )
    assert (
        validator.is_valid(f"{valid_aadhaar[:4]}-{valid_aadhaar[4:8]}-{valid_aadhaar[8:]}") is True
    )


def test_aadhaar_validator_invalid_starting_digits() -> None:
    validator = AadhaarValidator()
    # Aadhaar cannot start with 0 or 1
    aadhaar_with_0 = generate_valid_aadhaar("06759834256")
    aadhaar_with_1 = generate_valid_aadhaar("16759834256")
    assert validator.is_valid(aadhaar_with_0) is False
    assert validator.is_valid(aadhaar_with_1) is False


def test_aadhaar_validator_corrupt_checksum() -> None:
    validator = AadhaarValidator()
    valid_aadhaar = generate_valid_aadhaar("36759834256")
    # Invert the check digit
    corrupt_digit = str((int(valid_aadhaar[-1]) + 1) % 10)
    corrupted_aadhaar = valid_aadhaar[:-1] + corrupt_digit
    assert validator.is_valid(corrupted_aadhaar) is False


def test_aadhaar_validator_invalid_length_or_chars() -> None:
    validator = AadhaarValidator()
    assert validator.is_valid("12345678901") is False  # 11 digits
    assert validator.is_valid("1234567890123") is False  # 13 digits
    assert validator.is_valid("36759834256A") is False  # contains alpha


def test_aadhaar_masking() -> None:
    validator = AadhaarValidator()
    valid_aadhaar = generate_valid_aadhaar("36759834256")
    masked = validator.mask(valid_aadhaar)
    assert masked.startswith("XXXX-XXXX-")
    assert masked.endswith(valid_aadhaar[-4:])
    assert len(masked) == 14
