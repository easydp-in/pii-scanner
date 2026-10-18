"""Unit tests for find_all candidate scanning in unstructured text across all validators."""

from pii_scanner.validators.aadhaar import AadhaarValidator
from pii_scanner.validators.email import EmailValidator
from pii_scanner.validators.gstin import GSTINValidator, calculate_gstin_check_digit
from pii_scanner.validators.ifsc import IFSCValidator
from pii_scanner.validators.pan import PANValidator
from pii_scanner.validators.phone import IndianPhoneValidator
from pii_scanner.validators.upi import UPIValidator
from pii_scanner.validators.verhoeff import calculate_verhoeff


def test_find_all_in_text() -> None:
    # 1. Aadhaar
    aadhaar_val = AadhaarValidator()
    prefix = "36759834256"
    valid_aadhaar = prefix + calculate_verhoeff(prefix)
    text_aadhaar = f"Customer Aadhaar is {valid_aadhaar} and another fake is 111122223333."
    findings_aadhaar = aadhaar_val.find_all(text_aadhaar)
    assert len(findings_aadhaar) == 1
    assert findings_aadhaar[0][0] == valid_aadhaar
    assert findings_aadhaar[0][1].startswith("XXXX-XXXX-")

    # 2. PAN
    pan_val = PANValidator()
    text_pan = "Found PAN ABCPD1234F for Director and AAACR9999K for Corporate entity."
    findings_pan = pan_val.find_all(text_pan)
    assert len(findings_pan) == 2
    assert findings_pan[0][0] == "ABCPD1234F"
    assert findings_pan[0][2] == "Individual"
    assert findings_pan[1][0] == "AAACR9999K"
    assert findings_pan[1][2] == "Company"

    # 3. GSTIN
    gstin_val = GSTINValidator()
    gstin_prefix = "27AAACR1234A1Z"
    check = calculate_gstin_check_digit(gstin_prefix)
    valid_gstin = gstin_prefix + check
    text_gstin = f"Invoice GSTIN: {valid_gstin}."
    findings_gstin = gstin_val.find_all(text_gstin)
    assert len(findings_gstin) == 1
    assert findings_gstin[0][0] == valid_gstin

    # 4. IFSC
    ifsc_val = IFSCValidator()
    text_ifsc = "Transfer to SBIN0001234 via RTGS."
    findings_ifsc = ifsc_val.find_all(text_ifsc)
    assert len(findings_ifsc) == 1
    assert findings_ifsc[0][0] == "SBIN0001234"

    # 5. UPI
    upi_val = UPIValidator()
    text_upi = "Pay to merchant@okhdfcbank or refund@paytm."
    findings_upi = upi_val.find_all(text_upi)
    assert len(findings_upi) == 2

    # 6. Phone
    phone_val = IndianPhoneValidator()
    text_phone = "Contact customer care at +91 9876543210 or alternate 8123456789."
    findings_phone = phone_val.find_all(text_phone)
    assert len(findings_phone) == 2

    # 7. Email
    email_val = EmailValidator()
    text_email = "Email queries to info@easydp.in or support@company.co.in."
    findings_email = email_val.find_all(text_email)
    assert len(findings_email) == 2
