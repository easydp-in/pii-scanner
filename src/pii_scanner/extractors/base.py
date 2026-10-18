"""Base extractor interface and scan helpers for file analysis."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
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

    _DEFAULT_AADHAAR = AadhaarValidator()
    _DEFAULT_PAN = PANValidator()
    _DEFAULT_GSTIN = GSTINValidator()
    _DEFAULT_IFSC = IFSCValidator()
    _DEFAULT_UPI = UPIValidator()
    _DEFAULT_PHONE = IndianPhoneValidator()
    _DEFAULT_EMAIL = EmailValidator()

    def __init__(
        self,
        aadhaar_val: AadhaarValidator | None = None,
        pan_val: PANValidator | None = None,
        gstin_val: GSTINValidator | None = None,
        ifsc_val: IFSCValidator | None = None,
        upi_val: UPIValidator | None = None,
        phone_val: IndianPhoneValidator | None = None,
        email_val: EmailValidator | None = None,
    ) -> None:
        self.aadhaar_val = aadhaar_val or self._DEFAULT_AADHAAR
        self.pan_val = pan_val or self._DEFAULT_PAN
        self.gstin_val = gstin_val or self._DEFAULT_GSTIN
        self.ifsc_val = ifsc_val or self._DEFAULT_IFSC
        self.upi_val = upi_val or self._DEFAULT_UPI
        self.phone_val = phone_val or self._DEFAULT_PHONE
        self.email_val = email_val or self._DEFAULT_EMAIL

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
            return 0, datetime.now(timezone.utc)
        stat = p.stat()
        return stat.st_size, datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
