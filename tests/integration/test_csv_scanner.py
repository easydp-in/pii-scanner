"""Integration tests for CSV streaming extractor with various delimiters and encodings."""

from pathlib import Path

from pii_scanner.core.models import PIIType
from pii_scanner.extractors.csv_scanner import CSVExtractor
from pii_scanner.validators.verhoeff import calculate_verhoeff


def test_csv_scanner_detects_pii(tmp_path: Path) -> None:
    csv_file = tmp_path / "customers.csv"
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    content = (
        "Customer Name,Phone Number,Aadhaar,PAN\n"
        f"Rajesh Kumar,9876543210,{valid_aadhaar},ABCPD1234F\n"
        "Anita Rao,8123456789,111122223333,AAACR1234A\n"
    )
    csv_file.write_text(content, encoding="utf-8")

    extractor = CSVExtractor()
    result = extractor.extract(str(csv_file))

    assert result.is_sensitive is True
    assert result.findings_count >= 4
    assert result.findings_by_type[PIIType.AADHAAR.value] == 1  # 111122223333 is invalid checksum!
    assert result.findings_by_type[PIIType.PHONE.value] == 2
    assert result.findings_by_type[PIIType.PAN.value] == 2


def test_csv_semicolon_delimiter(tmp_path: Path) -> None:
    csv_file = tmp_path / "export_semicolon.csv"
    content = "Email;PAN\ncontact@easydp.in;ABCPD9999K\n"
    csv_file.write_text(content, encoding="utf-8")

    extractor = CSVExtractor()
    result = extractor.extract(str(csv_file))

    assert result.is_sensitive is True
    assert result.findings_by_type[PIIType.EMAIL.value] == 1
    assert result.findings_by_type[PIIType.PAN.value] == 1


def test_csv_clean_file(tmp_path: Path) -> None:
    csv_file = tmp_path / "clean_inventory.csv"
    content = "Item,SKU,Quantity,Price\nLaptop,SKU-100,10,50000\nKeyboard,SKU-101,25,1200\n"
    csv_file.write_text(content, encoding="utf-8")

    extractor = CSVExtractor()
    result = extractor.extract(str(csv_file))

    assert result.is_sensitive is False
    assert result.findings_count == 0
