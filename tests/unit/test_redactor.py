"""Unit tests for the centralized Redactor ensuring safe display with zero plaintext leaks."""

from pii_scanner.core.models import PIIType
from pii_scanner.core.redactor import Redactor


def test_redactor_masks_aadhaar() -> None:
    redactor = Redactor()
    raw = "367598342567"
    masked = redactor.mask(PIIType.AADHAAR, raw)
    assert masked.startswith("XXXX-XXXX-")
    assert raw not in masked
    assert masked.endswith("2567")


def test_redactor_masks_pan() -> None:
    redactor = Redactor()
    raw = "ABCPD1234F"
    masked = redactor.mask(PIIType.PAN, raw)
    assert masked == "XXXXX1234F"
    assert raw not in masked


def test_redactor_masks_gstin() -> None:
    redactor = Redactor()
    raw = "29AAACR1234A1Z5"
    masked = redactor.mask(PIIType.GSTIN, raw)
    assert "AAACR" not in masked
    assert masked.startswith("29XXXXX")


def test_redactor_masks_phone() -> None:
    redactor = Redactor()
    raw = "9876543210"
    masked = redactor.mask(PIIType.PHONE, raw)
    assert "98765" not in masked
    assert masked.endswith("43210")


def test_redactor_masks_ifsc() -> None:
    redactor = Redactor()
    raw = "SBIN0123456"
    masked = redactor.mask(PIIType.IFSC, raw)
    assert "123" not in masked
    assert masked == "SBIN0***456"


def test_redactor_masks_upi() -> None:
    redactor = Redactor()
    raw = "john.doe@okicici"
    masked = redactor.mask(PIIType.UPI, raw)
    assert "john.doe" not in masked
    assert "@okicici" in masked


def test_redactor_masks_email() -> None:
    redactor = Redactor()
    raw = "sarah.connor@sky.net"
    masked = redactor.mask(PIIType.EMAIL, raw)
    assert "sarah.connor" not in masked
    assert "@sky.net" in masked


def test_redactor_generic_fallback() -> None:
    redactor = Redactor()
    raw = "SecretValue123"
    masked = redactor.mask_generic(raw)
    assert masked == "S***3"
