"""Integration tests for document extractors: PDF, Word (.docx), OpenDocument (.odt), and RTF."""

import zipfile
from pathlib import Path

import pytest

from pii_scanner.core.engine import ScannerEngine
from pii_scanner.core.models import PIIType
from pii_scanner.extractors.docx_scanner import DocxExtractor
from pii_scanner.extractors.odt_scanner import ODTExtractor
from pii_scanner.extractors.pdf_scanner import PDFExtractor
from pii_scanner.extractors.rtf_scanner import RTFExtractor
from pii_scanner.validators.verhoeff import calculate_verhoeff


def test_pdf_text_extraction(tmp_path: Path) -> None:
    # Build a minimal raw PDF with text stream
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        b"4 0 obj <</Length 68>> stream\n"
        b"BT /F1 12 Tf 100 700 Td (Customer Aadhaar: " + valid_aadhaar.encode() + b") Tj ET\n"
        b"endstream endobj\n"
        b"5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000247 00000 n \n0000000366 00000 n \n"
        b"trailer <</Size 6 /Root 1 0 R>>\nstartxref\n443\n%%EOF"
    )
    pdf_file = tmp_path / "customer_receipt.pdf"
    pdf_file.write_bytes(pdf_content)

    extractor = PDFExtractor()
    result = extractor.extract(str(pdf_file))

    assert result.is_sensitive is True
    assert result.findings_by_type[PIIType.AADHAAR.value] == 1


def test_pdf_corrupted_file(tmp_path: Path) -> None:
    bad_pdf = tmp_path / "corrupt.pdf"
    bad_pdf.write_bytes(b"Not a real PDF header")

    extractor = PDFExtractor()
    result = extractor.extract(str(bad_pdf))
    assert result.is_sensitive is False
    assert result.error_message is not None


def test_docx_scanner_finds_pii(tmp_path: Path) -> None:
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    docx_file = tmp_path / "employment_contract.docx"

    with zipfile.ZipFile(docx_file, "w") as z:
        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body>"
            "<w:p><w:r><w:t>Employment Agreement with Jane Doe</w:t></w:r></w:p>"
            f"<w:p><w:r><w:t>Identity Card (Aadhaar): {valid_aadhaar}</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>Tax Identifier: ABCPD1234F | Contact: 9876543210</w:t></w:r></w:p>"
            "</w:body>"
            "</w:document>"
        )
        z.writestr("word/document.xml", doc_xml)

    extractor = DocxExtractor()
    result = extractor.extract(str(docx_file))

    assert result.is_sensitive is True
    assert result.findings_by_type[PIIType.AADHAAR.value] == 1
    assert result.findings_by_type[PIIType.PAN.value] == 1
    assert result.findings_by_type[PIIType.PHONE.value] == 1


def test_docx_clean_file(tmp_path: Path) -> None:
    docx_file = tmp_path / "clean_policy.docx"
    with zipfile.ZipFile(docx_file, "w") as z:
        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body>"
            "<w:p><w:r><w:t>Company Vacation and Leave Policy 2026</w:t></w:r></w:p>"
            "</w:body>"
            "</w:document>"
        )
        z.writestr("word/document.xml", doc_xml)

    extractor = DocxExtractor()
    result = extractor.extract(str(docx_file))

    assert result.is_sensitive is False
    assert result.findings_count == 0


def test_docx_corrupted(tmp_path: Path) -> None:
    bad_docx = tmp_path / "bad.docx"
    bad_docx.write_bytes(b"PK\x03\x04 corrupt zip bytes")

    extractor = DocxExtractor()
    result = extractor.extract(str(bad_docx))
    assert result.is_sensitive is False
    assert result.error_message is not None


def test_odt_scanner_finds_pii(tmp_path: Path) -> None:
    odt_file = tmp_path / "tax_filing.odt"
    with zipfile.ZipFile(odt_file, "w") as z:
        content_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            "<office:body>"
            "<office:text>"
            "<text:p>Business GSTIN registration: 27AABCU9603R1ZN</text:p>"
            "<text:p>Direct UPI settlement handle: merchant@okhdfcbank</text:p>"
            "</office:text>"
            "</office:body>"
            "</office:document-content>"
        )
        z.writestr("content.xml", content_xml)

    extractor = ODTExtractor()
    result = extractor.extract(str(odt_file))

    assert result.is_sensitive is True
    assert result.findings_by_type[PIIType.GSTIN.value] == 1
    assert result.findings_by_type[PIIType.UPI.value] == 1


def test_rtf_scanner_finds_pii(tmp_path: Path) -> None:
    rtf_file = tmp_path / "salary_slip.rtf"
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    rtf_content = (
        r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Courier;}}"
        r"\f0\fs20 Confidential Salary Certificate\par "
        rf"Employee Aadhaar: {valid_aadhaar}\par "
        r"PAN Number: ABCPD1234F\par "
        r"}"
    )
    rtf_file.write_text(rtf_content, encoding="utf-8")

    extractor = RTFExtractor()
    result = extractor.extract(str(rtf_file))

    assert result.is_sensitive is True
    assert result.findings_by_type[PIIType.AADHAAR.value] == 1
    assert result.findings_by_type[PIIType.PAN.value] == 1


def test_scanner_engine_discovers_all_documents(tmp_path: Path) -> None:
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")

    # 1. docx
    docx_file = tmp_path / "test.docx"
    with zipfile.ZipFile(docx_file, "w") as z:
        z.writestr(
            "word/document.xml",
            f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>{valid_aadhaar}</w:t></w:r></w:p></w:body></w:document>',
        )

    # 2. rtf
    rtf_file = tmp_path / "test.rtf"
    rtf_file.write_text(r"{\rtf1 PAN: ABCPD1234F}", encoding="utf-8")

    engine = ScannerEngine()
    summary = engine.scan_directory(str(tmp_path))

    assert summary.total_files_scanned >= 2
    assert summary.total_sensitive_files >= 2


def test_docx_decompression_guardrail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pii_scanner.extractors.docx_scanner.MAX_UNCOMPRESSED_ENTRY_SIZE", 10)
    docx_file = tmp_path / "bomb.docx"
    with zipfile.ZipFile(docx_file, "w") as z:
        z.writestr("word/document.xml", b"<document_longer_than_ten_bytes/>")

    extractor = DocxExtractor()
    result = extractor.extract(str(docx_file))

    assert result.is_sensitive is False
    assert result.error_message is not None
    assert "Decompression guardrail exceeded" in result.error_message


def test_odt_decompression_guardrail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pii_scanner.extractors.odt_scanner.MAX_UNCOMPRESSED_ENTRY_SIZE", 10)
    odt_file = tmp_path / "bomb.odt"
    with zipfile.ZipFile(odt_file, "w") as z:
        z.writestr("content.xml", b"<content_longer_than_ten_bytes/>")

    extractor = ODTExtractor()
    result = extractor.extract(str(odt_file))

    assert result.is_sensitive is False
    assert result.error_message is not None
    assert "Decompression guardrail exceeded" in result.error_message
