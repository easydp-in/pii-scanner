"""Integration tests for plain text, log files, and markdown extractor."""

from pathlib import Path

from pii_scanner.core.models import PIIType
from pii_scanner.extractors.text_scanner import TextExtractor
from pii_scanner.validators.verhoeff import calculate_verhoeff


def test_text_scanner_finds_pii(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    content = (
        f"2026-10-16 10:00:00 User registered with Aadhaar: {valid_aadhaar}\n"
        "2026-10-16 10:00:01 User PAN: ABCPD1234F provided for verification\n"
        "2026-10-16 10:00:02 OTP sent to mobile: 9876543210\n"
    )
    log_file.write_text(content, encoding="utf-8")

    extractor = TextExtractor()
    result = extractor.extract(str(log_file))

    assert result.is_sensitive is True
    assert result.findings_by_type[PIIType.AADHAAR.value] == 1
    assert result.findings_by_type[PIIType.PAN.value] == 1
    assert result.findings_by_type[PIIType.PHONE.value] == 1


def test_text_scanner_clean_file(tmp_path: Path) -> None:
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text(
        "General meeting notes discussing system architecture and Q4 goals.", encoding="utf-8"
    )

    extractor = TextExtractor()
    result = extractor.extract(str(txt_file))

    assert result.is_sensitive is False
    assert result.findings_count == 0
