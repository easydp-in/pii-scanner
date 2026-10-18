"""Unit tests for Person Name and Postal Address/PIN code validators."""

from pii_scanner.validators.address import AddressValidator
from pii_scanner.validators.email import EmailValidator
from pii_scanner.validators.person_name import PersonNameValidator
from pii_scanner.validators.upi import UPIValidator


def test_person_name_salutations() -> None:
    validator = PersonNameValidator()
    assert validator.is_valid("Mr. Rajesh Kumar") is True
    assert validator.is_valid("Dr. Sunita Rao") is True
    assert validator.is_valid("Ms. Priya Sharma") is True
    assert validator.is_valid("Shri Narendra Modi") is True
    assert validator.is_valid("Smt Nirmala Sitharaman") is True
    assert validator.is_valid("Prof. Vikram Sarabhai") is True


def test_person_name_labeled() -> None:
    validator = PersonNameValidator()
    assert validator.is_valid("Name: Amit Verma") is True
    assert validator.is_valid("Customer Name: Rohan Joshi") is True
    assert validator.is_valid("Employee Name: Sneha Patil") is True
    assert validator.is_valid("Full Name: Ananya Sen") is True


def test_person_name_column_context() -> None:
    validator = PersonNameValidator()
    # In a column named "Full Name" or "Customer Name"
    assert validator.is_valid("Ramesh Kumar", is_column_name=True) is True
    assert validator.is_valid("Deepak Chopra", is_column_name=True) is True
    # Without column context or salutation/label, a raw string without prefix is False
    assert validator.is_valid("Deepak Chopra", is_column_name=False) is False


def test_person_name_invalid_and_stopwords() -> None:
    validator = PersonNameValidator()
    # General words should not be detected as person names
    assert validator.is_valid("Total Amount: 50000") is False
    assert validator.is_valid("State: Karnataka") is False
    assert validator.is_valid("Invoice Number: 98213") is False
    assert validator.is_valid("Status: Active") is False
    assert validator.is_valid("John") is False  # single name too short/ambiguous
    assert validator.is_valid("12345 67890") is False


def test_person_name_masking() -> None:
    validator = PersonNameValidator()
    assert validator.mask("Mr. Rajesh Kumar") == "Mr. R***h K***r"
    assert validator.mask("Priyadarshini Rao") == "P***i R***o"
    assert validator.mask("Name: Rahul Sharma") == "Name: R***l S***a"


def test_address_pincode_validation() -> None:
    validator = AddressValidator()
    # Indian PIN codes
    assert validator.is_valid_pincode("560034") is True
    assert validator.is_valid_pincode("110001") is True
    assert validator.is_valid_pincode("400001") is True
    assert validator.is_valid_pincode("600001") is True
    # Invalid PIN codes
    assert validator.is_valid_pincode("012345") is False  # Starts with 0
    assert validator.is_valid_pincode("56003") is False   # 5 digits
    assert validator.is_valid_pincode("5600345") is False # 7 digits
    assert validator.is_valid_pincode("ABCDEF") is False


def test_address_physical_validation() -> None:
    validator = AddressValidator()
    assert validator.is_valid_address("Address: #123, 4th Cross, Indiranagar, Bengaluru 560038") is True
    assert validator.is_valid_address("Flat 402, Sunshine Apartments, MG Road, Pune - 411001") is True
    assert validator.is_valid_address("Plot 12, Sector 5, Salt Lake, Kolkata, West Bengal 700091") is True
    # Non-address text
    assert validator.is_valid_address("The quick brown fox jumps over the lazy dog") is False


def test_address_masking() -> None:
    validator = AddressValidator()
    assert validator.mask_pincode("560034") == "560***"
    assert validator.mask_pincode("110001") == "110***"
    masked_addr = validator.mask_address("Flat 402, Sunshine Apartments, MG Road, Pune - 411001")
    assert "Flat ***" in masked_addr
    assert "411***" in masked_addr


def test_upi_vs_email_distinction() -> None:
    upi_validator = UPIValidator()
    email_validator = EmailValidator()

    corporate_email = "support@easydp.io"
    user_email = "john.doe@company.com"
    academic_email = "student@iitb.ac.in"
    vpa_hdfc = "user@okhdfcbank"
    vpa_paytm = "9876543210@paytm"
    vpa_sbi = "customer@sbi"

    # Emails must NOT be valid UPI VPAs
    assert upi_validator.is_valid(corporate_email) is False
    assert upi_validator.is_valid(user_email) is False
    assert upi_validator.is_valid(academic_email) is False

    # Emails MUST be valid emails
    assert email_validator.is_valid(corporate_email) is True
    assert email_validator.is_valid(user_email) is True
    assert email_validator.is_valid(academic_email) is True

    # VPAs must be valid UPI VPAs
    assert upi_validator.is_valid(vpa_hdfc) is True
    assert upi_validator.is_valid(vpa_paytm) is True
    assert upi_validator.is_valid(vpa_sbi) is True
