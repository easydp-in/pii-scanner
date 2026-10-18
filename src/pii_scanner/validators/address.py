"""Indian Postal Address and 6-digit PIN Code validator and redactor."""

from __future__ import annotations

import re

# Explicit PIN code label prefixes
EXPLICIT_PIN_REGEX = re.compile(
    r"(?i:\b(?:PIN(?:\s*Code)?|Postal\s*Code|Zip(?:\s*Code)?|Pincode)[\s:-]+)([1-9][0-9]{2}\s?[0-9]{3})\b"
)

# Major Indian Cities and States for contextual PIN detection
INDIAN_CITIES_STATES = (
    r"(?:Delhi|New\s+Delhi|Mumbai|Bengaluru|Bangalore|Kolkata|Calcutta|Chennai|Madras|"
    r"Hyderabad|Pune|Ahmedabad|Jaipur|Surat|Lucknow|Kanpur|Nagpur|Indore|Thane|Bhopal|"
    r"Visakhapatnam|Patna|Vadodara|Ghaziabad|Ludhiana|Agra|Nashik|Faridabad|Meerut|Rajkot|"
    r"Varanasi|Srinagar|Aurangabad|Dhanbad|Amritsar|Navi\s+Mumbai|Allahabad|Prayagraj|"
    r"Ranchi|Howrah|Coimbatore|Jabalpur|Gwalior|Vijayawada|Jodhpur|Madurai|Raipur|Kota|"
    r"Guwahati|Chandigarh|Solapur|Hubli|Dharwad|Bareilly|Moradabad|Mysore|Mysuru|Gurgaon|"
    r"Gurugram|Noida|Karnataka|Maharashtra|Tamil\s+Nadu|Uttar\s+Pradesh|Gujarat|Rajasthan|"
    r"West\s+Bengal|Madhya\s+Pradesh|Andhra\s+Pradesh|Telangana|Kerala|Bihar|Punjab|Haryana|"
    r"Odisha|Orissa|Assam|Jharkhand|Chhattisgarh|Uttarakhand|Himachal\s+Pradesh|Goa)"
)

CITY_STATE_PIN_REGEX = re.compile(
    rf"\b({INDIAN_CITIES_STATES}[\s,-]+(?:[A-Za-z\s,-]{{0,35}}[\s,-]+)?([1-9][0-9]{{2}}\s?[0-9]{{3}}))\b",
    re.IGNORECASE,
)

ADDRESS_LINE_REGEX = re.compile(
    r"(?i:\b(?:Address|Res\.\s*Address|Permanent\s*Address|Billing\s*Address|Shipping\s*Address|Communication\s*Address|Registered\s*Office)[\s:-]+)([^\n\r,]+(?:,[^\n\r,]+){1,5})\b"
)


class AddressValidator:
    """Validates and masks Indian postal addresses and 6-digit PIN codes."""

    def is_valid_pincode(self, value: str) -> bool:
        """Validate if a string is a standard 6-digit Indian PIN code."""
        cleaned = re.sub(r"\s+", "", value.strip())
        if len(cleaned) != 6 or not cleaned.isdigit():
            return False
        # First digit represents Indian postal zone (1-9, never 0)
        return cleaned[0] in "123456789"

    def mask_pincode(self, pincode: str) -> str:
        """Mask 6-digit PIN code: 560034 -> 560***."""
        clean = re.sub(r"\s+", "", pincode.strip())
        if len(clean) == 6:
            return f"{clean[:3]}***"
        return "XXXXXX"

    def is_valid_address(self, address: str) -> bool:
        """Validate if a string is a recognizable postal address."""
        clean = address.strip()
        if len(clean) < 12:
            return False

        # If it begins with an address label prefix
        if ADDRESS_LINE_REGEX.search(clean):
            return True

        # Has commas and address keywords
        lower = clean.lower()
        has_kw = any(
            k in lower
            for k in (
                "road", "street", "nagar", "colony", "layout", "sector",
                "flat", "plot", "floor", "building", "tower", "cross", "main",
                "apartment", "apartments", "block", "lane",
            )
        )
        has_pin = bool(re.search(r"\b[1-9][0-9]{5}\b", clean))
        has_num = any(c.isdigit() for c in clean)

        return (has_kw and (has_num or has_pin)) or (has_pin and len(clean.split(",")) >= 2)

    def mask_address(self, address: str) -> str:
        """Mask address line preserving general locality and masking specific numbers & pin."""
        clean = address.strip()
        # First mask any 6-digit PIN code
        clean = re.sub(r"\b([1-9][0-9]{2})[0-9]{3}\b", r"\1***", clean)

        parts = [p.strip() for p in clean.split(",") if p.strip()]
        if len(parts) <= 1:
            return "Plot ***, [Address Protected]"
        masked_first = re.sub(r"\d+", "***", parts[0])
        return ", ".join([masked_first] + parts[1:])

    def find_all_pincodes(self, text: str) -> list[tuple[str, str]]:
        """Find Indian PIN codes with contextual validation."""
        results: list[tuple[str, str]] = []
        seen: set[str] = set()

        for match in EXPLICIT_PIN_REGEX.finditer(text):
            code = match.group(1).replace(" ", "")
            if self.is_valid_pincode(code) and code not in seen:
                seen.add(code)
                results.append((code, self.mask_pincode(code)))

        for match in CITY_STATE_PIN_REGEX.finditer(text):
            code = match.group(2).replace(" ", "")
            if self.is_valid_pincode(code) and code not in seen:
                seen.add(code)
                results.append((code, self.mask_pincode(code)))

        return results

    def find_all_addresses(self, text: str) -> list[tuple[str, str]]:
        """Find postal address blocks in text."""
        results: list[tuple[str, str]] = []
        seen: set[str] = set()

        for match in ADDRESS_LINE_REGEX.finditer(text):
            addr = match.group(1).strip()
            if len(addr) >= 12 and (
                any(c.isdigit() for c in addr)
                or any(
                    k in addr.lower()
                    for k in (
                        "road", "street", "nagar", "colony", "layout", "sector",
                        "flat", "plot", "floor", "building", "tower", "cross", "main",
                    )
                )
            ):
                if addr not in seen:
                    seen.add(addr)
                    results.append((addr, self.mask_address(addr)))

        return results
