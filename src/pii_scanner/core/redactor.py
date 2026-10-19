"""Centralized Redactor ensuring all sensitive values are safely masked before logging or display."""

from collections.abc import Callable

from pii_scanner.core.models import PIIType
from pii_scanner.validators.aadhaar import AadhaarValidator
from pii_scanner.validators.address import AddressValidator
from pii_scanner.validators.email import EmailValidator
from pii_scanner.validators.gstin import GSTINValidator
from pii_scanner.validators.ifsc import IFSCValidator
from pii_scanner.validators.pan import PANValidator
from pii_scanner.validators.person_name import PersonNameValidator
from pii_scanner.validators.phone import IndianPhoneValidator
from pii_scanner.validators.upi import UPIValidator


class Redactor:
    """Provides consistent, audit-compliant redaction across all PII data types."""

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

        self._mask_dispatch: dict[PIIType, Callable[[str], str]] = {
            PIIType.AADHAAR: self.aadhaar_val.mask,
            PIIType.PAN: self.pan_val.mask,
            PIIType.NAME: self.name_val.mask,
            PIIType.GSTIN: self.gstin_val.mask,
            PIIType.IFSC: self.ifsc_val.mask,
            PIIType.UPI: self.upi_val.mask,
            PIIType.PHONE: self.phone_val.mask,
            PIIType.EMAIL: self.email_val.mask,
            PIIType.ADDRESS: self.address_val.mask_address,
            PIIType.PINCODE: self.address_val.mask_pincode,
            PIIType.HEALTH: self.mask_generic,
        }

    def mask(self, pii_type: PIIType, raw_value: str) -> str:
        """Mask a sensitive value according to its statutory or domain rules."""
        mask_fn = self._mask_dispatch.get(pii_type)
        if mask_fn:
            return mask_fn(raw_value)
        return self.mask_generic(raw_value)

    @staticmethod
    def mask_generic(raw_value: str) -> str:
        """Generic fallback masking keeping only first and last characters."""
        val = raw_value.strip()
        if len(val) <= 2:
            return "***"
        return f"{val[0]}***{val[-1]}"
