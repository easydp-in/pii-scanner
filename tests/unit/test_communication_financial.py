"""Unit tests for Indian Bank IFSC, UPI VPA, Phone, and Email validators."""

from pii_scanner.validators.email import EmailValidator
from pii_scanner.validators.ifsc import IFSCValidator
from pii_scanner.validators.phone import IndianPhoneValidator
from pii_scanner.validators.upi import UPIValidator


def test_ifsc_valid() -> None:
    validator = IFSCValidator()
    # 4 alpha, 0, 6 alnum
    assert validator.is_valid("SBIN0001234") is True
    assert validator.is_valid("HDFC0000001") is True
    assert validator.is_valid("ICIC0001999") is True


def test_ifsc_invalid() -> None:
    validator = IFSCValidator()
    assert validator.is_valid("SBIN1001234") is False  # 5th char not '0'
    assert validator.is_valid("SBI00001234") is False  # 3 alpha instead of 4
    assert validator.is_valid("SBIN000123") is False  # too short


def test_ifsc_masking() -> None:
    validator = IFSCValidator()
    masked = validator.mask("SBIN0001234")
    assert masked == "SBIN0***234"


def test_upi_valid() -> None:
    validator = UPIValidator()
    assert validator.is_valid("merchant@okhdfcbank") is True
    assert validator.is_valid("9876543210@paytm") is True
    assert validator.is_valid("john.doe@oksbi") is True
    assert validator.is_valid("user_123@ybl") is True


def test_upi_invalid() -> None:
    validator = UPIValidator()
    assert validator.is_valid("invalid-vpa") is False
    assert validator.is_valid("@okhdfcbank") is False
    assert validator.is_valid("merchant@") is False


def test_upi_masking() -> None:
    validator = UPIValidator()
    masked = validator.mask("john.doe@okhdfcbank")
    assert masked == "j***e@okhdfcbank"


def test_phone_valid_indian_numbers() -> None:
    validator = IndianPhoneValidator()
    assert validator.is_valid("9876543210") is True
    assert validator.is_valid("+91 9876543210") is True
    assert validator.is_valid("+91-98765-43210") is True
    assert validator.is_valid("09876543210") is True
    assert validator.is_valid("8123456789") is True
    assert validator.is_valid("7123456789") is True
    assert validator.is_valid("6123456789") is True


def test_phone_invalid_indian_numbers() -> None:
    validator = IndianPhoneValidator()
    assert validator.is_valid("5123456789") is False  # Starts with 5
    assert validator.is_valid("1234567890") is False  # Starts with 1
    assert validator.is_valid("987654321") is False  # 9 digits
    assert validator.is_valid("987654321000") is False  # 12 digits without country code


def test_phone_masking() -> None:
    validator = IndianPhoneValidator()
    masked = validator.mask("+91 9876543210")
    assert masked == "+91-XXXXX-43210"


def test_email_valid() -> None:
    validator = EmailValidator()
    assert validator.is_valid("john.doe@company.com") is True
    assert validator.is_valid("user_123@sub.example.co.in") is True


def test_email_invalid() -> None:
    validator = EmailValidator()
    assert validator.is_valid("plainaddress") is False
    assert validator.is_valid("@missingusername.com") is False
    assert validator.is_valid("username@.com") is False


def test_email_masking() -> None:
    validator = EmailValidator()
    masked = validator.mask("priya.sharma@example.com")
    assert masked == "p***a@example.com"
