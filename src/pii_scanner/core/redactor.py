"""Centralized Redactor ensuring all sensitive values are safely masked before logging or display."""

from pii_scanner.core.models import PIIType
from pii_scanner.validators.aadhaar import AadhaarValidator
from pii_scanner.validators.email import EmailValidator
from pii_scanner.validators.gstin import GSTINValidator
from pii_scanner.validators.ifsc import IFSCValidator
from pii_scanner.validators.pan import PANValidator
from pii_scanner.validators.phone import IndianPhoneValidator
from pii_scanner.validators.upi import UPIValidator


class Redactor:
    """Provides consistent, audit-compliant redaction across all PII data types."""

    def __init__(self) -> None:
        self.aadhaar_val = AadhaarValidator()
        self.pan_val = PANValidator()
        self.gstin_val = GSTINValidator()
        self.ifsc_val = IFSCValidator()
        self.upi_val = UPIValidator()
        self.phone_val = IndianPhoneValidator()
        self.email_val = EmailValidator()

    def mask(self, pii_type: PIIType, raw_value: str) -> str:
        """Mask a sensitive value according to its statutory or domain rules."""
        if pii_type == PIIType.AADHAAR:
            return self.aadhaar_val.mask(raw_value)
        if pii_type == PIIType.PAN:
            return self.pan_val.mask(raw_value)
        if pii_type == PIIType.GSTIN:
            return self.gstin_val.mask(raw_value)
        if pii_type == PIIType.IFSC:
            return self.ifsc_val.mask(raw_value)
        if pii_type == PIIType.UPI:
            return self.upi_val.mask(raw_value)
        if pii_type == PIIType.PHONE:
            return self.phone_val.mask(raw_value)
        if pii_type == PIIType.EMAIL:
            return self.email_val.mask(raw_value)
        return self.mask_generic(raw_value)

    @staticmethod
    def mask_generic(raw_value: str) -> str:
        """Generic fallback masking keeping only first and last characters."""
        val = raw_value.strip()
        if len(val) <= 2:
            return "***"
        return f"{val[0]}***{val[-1]}"
