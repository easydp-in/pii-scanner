"""Integration tests for Excel (.xlsx) extractor."""

from pathlib import Path

import openpyxl

from pii_scanner.core.models import PIIType
from pii_scanner.extractors.excel_scanner import ExcelExtractor
from pii_scanner.validators.gstin import calculate_gstin_check_digit


def test_excel_scanner_detects_pii(tmp_path: Path) -> None:
    xlsx_file = tmp_path / "accounts.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = "Vendors"

    gstin_prefix = "29AAACR1234A1Z"
    valid_gstin = gstin_prefix + calculate_gstin_check_digit(gstin_prefix)

    # Headers
    ws.append(["Vendor Name", "GSTIN", "IFSC Code", "Contact Email"])
    # Row 1
    ws.append(["ABC Enterprises", valid_gstin, "HDFC0000001", "accounts@abcenterprises.com"])
    # Row 2 (Clean)
    ws.append(["General Supplier", "N/A", "N/A", "N/A"])

    wb.save(xlsx_file)

    extractor = ExcelExtractor()
    result = extractor.extract(str(xlsx_file))

    assert result.is_sensitive is True
    assert result.findings_by_type[PIIType.GSTIN.value] == 1
    assert result.findings_by_type[PIIType.IFSC.value] == 1
    assert result.findings_by_type[PIIType.EMAIL.value] == 1


def test_excel_clean_file(tmp_path: Path) -> None:
    xlsx_file = tmp_path / "budget.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.append(["Department", "Q1 Budget", "Q2 Budget"])
    ws.append(["Engineering", 500000, 600000])
    wb.save(xlsx_file)

    extractor = ExcelExtractor()
    result = extractor.extract(str(xlsx_file))

    assert result.is_sensitive is False
    assert result.findings_count == 0
