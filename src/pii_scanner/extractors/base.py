"""Base extractor interface and scan helpers for file analysis."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

from pii_scanner.core.models import FileScanResult, Finding, PIIType
from pii_scanner.validators.aadhaar import AadhaarValidator
from pii_scanner.validators.address import AddressValidator
from pii_scanner.validators.email import EmailValidator
from pii_scanner.validators.gstin import GSTINValidator
from pii_scanner.validators.ifsc import IFSCValidator
from pii_scanner.validators.pan import PANValidator
from pii_scanner.validators.person_name import PersonNameValidator
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
    _DEFAULT_NAME = PersonNameValidator()
    _DEFAULT_ADDRESS = AddressValidator()

    def __init__(
        self,
        aadhaar_val: AadhaarValidator | None = None,
        pan_val: PANValidator | None = None,
        gstin_val: GSTINValidator | None = None,
        ifsc_val: IFSCValidator | None = None,
        upi_val: UPIValidator | None = None,
        phone_val: IndianPhoneValidator | None = None,
        email_val: EmailValidator | None = None,
        name_val: PersonNameValidator | None = None,
        address_val: AddressValidator | None = None,
    ) -> None:
        self.aadhaar_val = aadhaar_val or self._DEFAULT_AADHAAR
        self.pan_val = pan_val or self._DEFAULT_PAN
        self.gstin_val = gstin_val or self._DEFAULT_GSTIN
        self.ifsc_val = ifsc_val or self._DEFAULT_IFSC
        self.upi_val = upi_val or self._DEFAULT_UPI
        self.phone_val = phone_val or self._DEFAULT_PHONE
        self.email_val = email_val or self._DEFAULT_EMAIL
        self.name_val = name_val or self._DEFAULT_NAME
        self.address_val = address_val or self._DEFAULT_ADDRESS

    @abstractmethod
    def extract(self, file_path: str) -> FileScanResult:
        """Scan a file or source and return structured findings."""
        pass

    def scan_text_segment(
        self, text: str, location_prefix: str, column_name: str | None = None
    ) -> list[Finding]:
        """Inspect a string segment against all registered validators."""
        findings: list[Finding] = []
        text_clean = text.strip()
        if not text_clean:
            return findings

        # Contextual column matching for tabular spreadsheets and CSVs
        if column_name:
            col_lower = column_name.lower().strip()
            # 1. Person Name column
            if any(
                k in col_lower
                for k in (
                    "name", "full name", "customer name", "employee name",
                    "candidate name", "client name", "patient name", "student name",
                    "applicant name", "contact person", "director name",
                    "nominee name", "father name", "mother name", "spouse name",
                )
            ) and not any(k in col_lower for k in ("company", "bank", "file", "folder", "org", "user")):
                if self.name_val.is_valid_name(text_clean):
                    findings.append(
                        Finding(
                            pii_type=PIIType.NAME,
                            masked_value=self.name_val.mask(text_clean),
                            location=location_prefix,
                            confidence=0.95,
                        )
                    )

            # 2. Postal Address column
            if any(
                k in col_lower
                for k in (
                    "address", "street", "residential address", "permanent address",
                    "billing address", "shipping address", "communication address",
                )
            ):
                if len(text_clean) >= 6:
                    findings.append(
                        Finding(
                            pii_type=PIIType.ADDRESS,
                            masked_value=self.address_val.mask_address(text_clean),
                            location=location_prefix,
                            confidence=0.95,
                        )
                    )

            # 3. PIN Code column
            if any(k in col_lower for k in ("pin", "pincode", "pin code", "postal code", "zip", "zip code", "zipcode")):
                clean_digits = text_clean.replace(" ", "")
                if self.address_val.is_valid_pincode(clean_digits):
                    findings.append(
                        Finding(
                            pii_type=PIIType.PINCODE,
                            masked_value=self.address_val.mask_pincode(clean_digits),
                            location=location_prefix,
                            confidence=1.0,
                        )
                    )

        # Standard Content / Unstructured Regex Validations
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

        # 5. Email (Executed BEFORE UPI so emails are never counted as VPAs)
        for _raw, masked in self.email_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.EMAIL,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=0.95,
                )
            )

        # 6. UPI VPA Handle
        for _raw, masked in self.upi_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.UPI,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=1.0,
                )
            )

        # 7. Indian Mobile Phone
        for _raw, masked in self.phone_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.PHONE,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=0.95,
                )
            )

        # 8. Person Names in document text
        for _raw, masked in self.name_val.find_all(text):
            findings.append(
                Finding(
                    pii_type=PIIType.NAME,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=0.90,
                )
            )

        # 9. Postal Address blocks in document text
        for _raw, masked in self.address_val.find_all_addresses(text):
            findings.append(
                Finding(
                    pii_type=PIIType.ADDRESS,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=0.90,
                )
            )

        # 10. Indian PIN Codes in document text
        for _raw, masked in self.address_val.find_all_pincodes(text):
            findings.append(
                Finding(
                    pii_type=PIIType.PINCODE,
                    masked_value=masked,
                    location=location_prefix,
                    confidence=0.95,
                )
            )

        # Deduplicate findings with identical (pii_type, masked_value, location)
        unique_findings: list[Finding] = []
        seen_keys: set[tuple[PIIType, str, str]] = set()
        for f in findings:
            key = (f.pii_type, f.masked_value, f.location)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_findings.append(f)

        return unique_findings

    @staticmethod
    def get_file_metadata(file_path: str) -> tuple[int, datetime]:
        p = Path(file_path)
        if not p.exists():
            return 0, datetime.now(timezone.utc)
        stat = p.stat()
        return stat.st_size, datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
