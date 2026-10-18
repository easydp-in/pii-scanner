"""Extractors for files and accounting databases."""

from pii_scanner.extractors.base import BaseExtractor
from pii_scanner.extractors.csv_scanner import CSVExtractor
from pii_scanner.extractors.excel_scanner import ExcelExtractor
from pii_scanner.extractors.tally import TallyConnector
from pii_scanner.extractors.text_scanner import TextExtractor

__all__ = [
    "BaseExtractor",
    "CSVExtractor",
    "ExcelExtractor",
    "TextExtractor",
    "TallyConnector",
]
