"""Extractors for files and accounting databases."""

from pii_scanner.extractors.base import BaseExtractor
from pii_scanner.extractors.csv_scanner import CSVExtractor
from pii_scanner.extractors.docx_scanner import DocxExtractor
from pii_scanner.extractors.excel_scanner import ExcelExtractor
from pii_scanner.extractors.odt_scanner import ODTExtractor
from pii_scanner.extractors.pdf_scanner import PDFExtractor
from pii_scanner.extractors.rtf_scanner import RTFExtractor
from pii_scanner.extractors.tally import TallyConnector
from pii_scanner.extractors.text_scanner import TextExtractor

__all__ = [
    "BaseExtractor",
    "CSVExtractor",
    "DocxExtractor",
    "ExcelExtractor",
    "ODTExtractor",
    "PDFExtractor",
    "RTFExtractor",
    "TallyConnector",
    "TextExtractor",
]
