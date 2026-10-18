"""Base extractor interface and scan helpers for file analysis."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from pii_scanner.core.models import FileScanResult, Finding, PIIType
from pii_scanner.validators.aadhaar import AadhaarValidator
from pii_scanner.validators.email import EmailValidator
from pii_scanner.validators.gstin import GSTINValidator
from pii_scanner.validators.ifsc import IFSCValidator
from pii_scanner.validators.pan import PANValidator
from pii_scanner.validators.phone import IndianPhoneValidator
from pii_scanner.validators.upi import UPIValidator


class BaseExtractor(ABC):
    """Abstract base class for all file and data source extractors."""

    def __init__(self) -> None:
        self.aadhaar_val = AadhaarValidator()
        self.pan_val = PANValidator()
        self.gstin_val = GSTINValidator()
        self.ifsc_val = IFSCValidator()
        self.upi_val = UPIValidator()
        self.phone_val = IndianPhoneValidator()
        self.email_val = EmailValidator()

    @abstractmethod
    def extract(self, file_path: str) -> FileScanResult:
        """Scan a file or source and return structured findings."""
        pass

    def scan_text_segment(self, text: str, location_prefix: str) -> list[Finding]:
        """Inspect a string segment against all registered validators."""
        findings: list[Finding] = []

        # 1. Aadhaar
        for _raw, masked in self.aadhaar_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.AADHAAR,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=1.0,
                )
            )

        # 2. PAN
        for _raw, masked, entity in self.pan_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.PAN,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=1.0,
                    entity_info=entity,
                )
            )

        # 3. GSTIN
        for _raw, masked in self.gstin_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.GSTIN,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=1.0,
                )
            )

        # 4. IFSC
        for _raw, masked in self.ifsc_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.IFSC,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=1.0,
                )
            )

        # 5. UPI
        for _raw, masked in self.upi_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.UPI,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=1.0,
                )
            )

        # 6. Phone
        for _raw, masked in self.phone_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.PHONE,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=0.95,
                )
            )

        # 7. Email
        for _raw, masked in self.email_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.EMAIL,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=0.95,
                )
            )

        return findings

    @staticmethod
    def get_file_metadata(file_path: str) -> tuple[int, datetime]:
        p = Path(file_path)
        if not p.exists():
            return 0, datetime.now()
        stat = p.stat()
        return stat.st_size, datetime.fromtimestamp(stat.st_mtime)
