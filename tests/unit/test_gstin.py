"""Unit tests for Indian GSTIN (Goods and Services Tax Identification Number) validation."""

from pii_scanner.validators.gstin import GSTINValidator, calculate_gstin_check_digit


def test_calculate_gstin_check_digit() -> None:
    # 14 chars prefix
    prefix = "27AAACR1234A1Z"
    check = calculate_gstin_check_digit(prefix)
    assert len(check) == 1
    assert check.isalnum()


def test_gstin_valid_structure_and_checksum() -> None:
    validator = GSTINValidator()
    # Construct a valid GSTIN
    prefix = "29AAACR1234A1Z"
    check = calculate_gstin_check_digit(prefix)
    valid_gstin = prefix + check
    assert validator.is_valid(valid_gstin) is True


def test_gstin_invalid_state_code() -> None:
    validator = GSTINValidator()
    # 00 and 98 are invalid state codes
    assert validator.is_valid("00AAACR1234A1Z5") is False
    assert validator.is_valid("98AAACR1234A1Z5") is False


def test_gstin_invalid_14th_char() -> None:
    validator = GSTINValidator()
    # 14th char must be 'Z'
    prefix = "27AAACR1234A1A"
    check = calculate_gstin_check_digit(prefix)
    assert validator.is_valid(prefix + check) is False


def test_gstin_corrupted_check_digit() -> None:
    validator = GSTINValidator()
    prefix = "29AAACR1234A1Z"
    correct_check = calculate_gstin_check_digit(prefix)
    wrong_check = "0" if correct_check != "0" else "1"
    assert validator.is_valid(prefix + wrong_check) is False


def test_gstin_masking() -> None:
    validator = GSTINValidator()
    prefix = "29AAACR1234A1Z"
    check = calculate_gstin_check_digit(prefix)
    full_gstin = prefix + check
    masked = validator.mask(full_gstin)
    # Mask embedded PAN: 29XXXXX1234X1Z<check>
    assert masked.startswith("29XXXXX")
    assert masked.endswith(f"1Z{check}")
