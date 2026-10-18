"""Integration tests for ScannerEngine directory traversal and data inventory aggregation."""

from pathlib import Path

from pii_scanner.core.engine import ScannerEngine
from pii_scanner.core.models import PIICategory, PIIType
from pii_scanner.validators.gstin import calculate_gstin_check_digit
from pii_scanner.validators.verhoeff import calculate_verhoeff


def test_scanner_engine_directory_scan(tmp_path: Path) -> None:
    # 1. Create a customer CSV
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(
        f"Name,Aadhaar,PAN\nJohn Doe,{valid_aadhaar},ABCPD1234F\n", encoding="utf-8"
    )

    # 2. Create a clean notes file
    clean_file = tmp_path / "meeting_notes.txt"
    clean_file.write_text("Discussed project roadmap and release schedules.", encoding="utf-8")

    # 3. Create a financial file with GSTIN
    gstin_prefix = "27AAACR1234A1Z"
    valid_gstin = gstin_prefix + calculate_gstin_check_digit(gstin_prefix)
    gstin_file = tmp_path / "invoices.txt"
    gstin_file.write_text(
        f"Vendor GSTIN: {valid_gstin}\nContact: +91 9876543210\n", encoding="utf-8"
    )

    engine = ScannerEngine()
    summary = engine.scan_directory(str(tmp_path))

    assert summary.total_files_scanned == 3
    assert summary.total_sensitive_files == 2
    assert summary.total_clean_files == 1
    assert summary.total_pii_instances >= 4

    # Check categories
    assert summary.by_category[PIICategory.IDENTITY.value] >= 2
    assert summary.by_category[PIICategory.FINANCIAL.value] >= 1
    assert summary.by_category[PIICategory.CONTACT.value] >= 1

    # Check specific types
    assert summary.by_type[PIIType.AADHAAR.value] == 1
    assert summary.by_type[PIIType.PAN.value] == 1
    assert summary.by_type[PIIType.GSTIN.value] == 1
    assert summary.by_type[PIIType.PHONE.value] == 1


def test_scanner_engine_respects_exclusions(tmp_path: Path) -> None:
    # Ignored directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    git_file = git_dir / "config.txt"
    git_file.write_text("Phone: 9876543210\n", encoding="utf-8")

    clean_file = tmp_path / "doc.txt"
    clean_file.write_text("Hello World", encoding="utf-8")

    engine = ScannerEngine()
    summary = engine.scan_directory(str(tmp_path))

    # .git should be ignored by default
    assert summary.total_files_scanned == 1
    assert summary.total_sensitive_files == 0


def test_scanner_engine_multiple_directories(tmp_path: Path) -> None:
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    (dir1 / "file1.txt").write_text("Contact: 9876543210", encoding="utf-8")

    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    (dir2 / "file2.txt").write_text("Clean file content", encoding="utf-8")

    engine = ScannerEngine()
    summary = engine.scan_directories([str(dir1), str(dir2)])

    assert summary.total_files_scanned == 2
    assert summary.total_sensitive_files == 1
    assert summary.total_clean_files == 1
    assert summary.total_pii_instances == 1


def test_extractor_registry_custom_registration(tmp_path: Path) -> None:
    from pii_scanner.core.engine import ExtractorRegistry
    from pii_scanner.extractors.text_scanner import TextExtractor

    registry = ExtractorRegistry()
    assert ".csv" in registry
    assert ".txt" in registry

    # Register custom extension .customlog
    registry.register(".customlog", TextExtractor)
    assert ".customlog" in registry
    assert isinstance(registry.get(".customlog"), TextExtractor)
    assert ".customlog" in registry.supported_extensions()

    # Scan with custom registry
    engine = ScannerEngine(registry=registry)
    custom_file = tmp_path / "app.customlog"
    custom_file.write_text("Admin: 9876543210", encoding="utf-8")
    summary = engine.scan_directory(str(tmp_path))

    assert summary.total_files_scanned == 1
    assert summary.total_sensitive_files == 1
    assert summary.total_pii_instances == 1


def test_scanner_engine_timezone_naive_resilience(tmp_path: Path) -> None:
    from datetime import datetime
    from unittest.mock import patch

    from pii_scanner.core.models import FileScanResult

    # Mock extract to return naive modified_time
    clean_file = tmp_path / "naive.txt"
    clean_file.write_text("Phone: 9876543210", encoding="utf-8")

    engine = ScannerEngine()
    dummy_res = FileScanResult(
        file_path=str(clean_file),
        file_name="naive.txt",
        file_size_bytes=100,
        modified_time=datetime(2020, 1, 1, 12, 0, 0),  # naive datetime
        is_sensitive=True,
        findings_count=1,
        findings_by_type={PIIType.PHONE.value: 1},
    )

    with patch.object(engine.registry.get(".txt"), "extract", return_value=dummy_res):
        summary = engine.scan_directory(str(tmp_path))
        # Staleness should calculate without raising TypeError
        assert summary.stale_files_over_3y >= 1


def test_scanner_engine_skipped_targets(tmp_path: Path) -> None:
    dir1 = tmp_path / "valid_dir"
    dir1.mkdir()
    (dir1 / "note.txt").write_text("Hello", encoding="utf-8")

    non_existent = str(tmp_path / "does_not_exist")

    engine = ScannerEngine()
    summary = engine.scan_directories([str(dir1), non_existent])

    assert summary.total_files_scanned == 1
    assert len(summary.skipped_targets) == 1
    assert "does_not_exist" in summary.skipped_targets[0]
