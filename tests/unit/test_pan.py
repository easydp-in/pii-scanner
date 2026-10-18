"""Unit tests for Indian PAN (Permanent Account Number) validation and redaction."""

from pii_scanner.validators.pan import PANValidator


def test_pan_valid_individual() -> None:
    validator = PANValidator()
    # P for individual
    assert validator.is_valid("ABCDE1234F") is False  # 'E' is not a valid 4th char
    assert validator.is_valid("ABCPD1234F") is True  # 'P' is Person
    assert validator.is_valid("xyzpc5678k") is True  # Case insensitive handling


def test_pan_valid_entities() -> None:
    validator = PANValidator()
    # C=Company, H=HUF, F=Firm, T=Trust, G=Government
    assert validator.is_valid("AAACR1234A") is True  # Company
    assert validator.is_valid("AAAFR1234A") is True  # Firm
    assert validator.is_valid("AAATR1234A") is True  # Trust
    assert validator.is_valid("AAAGR1234A") is True  # Government


def test_pan_invalid_patterns() -> None:
    validator = PANValidator()
    assert validator.is_valid("ABCP12345F") is False  # too many numbers
    assert validator.is_valid("ABCP123F") is False  # too few numbers
    assert validator.is_valid("12345ABCDE") is False  # wrong order
    assert validator.is_valid("ABCPD12345") is False  # ends in digit instead of char


def test_pan_entity_type_extraction() -> None:
    validator = PANValidator()
    assert validator.get_entity_type("ABCPD1234F") == "Individual"
    assert validator.get_entity_type("AAACR1234A") == "Company"
    assert validator.get_entity_type("AAAFR1234A") == "Firm / LLP"
    assert validator.get_entity_type("INVALID123") == "Unknown"


def test_pan_masking() -> None:
    validator = PANValidator()
    masked = validator.mask("ABCPD1234F")
    assert masked == "XXXXX1234F"
