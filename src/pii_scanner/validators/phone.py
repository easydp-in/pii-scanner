"""Indian mobile phone number validator and redactor."""

import re

# Indian phone regex: standalone 10 digits starting with 6-9, with optional +91, 91, or 0 prefix
PHONE_REGEX = re.compile(r"(?<!\d)(?:(?:\+91|91|0)[\s\-]?)?([6-9]\d{4}[\s\-]?\d{5})(?!\d)")


class IndianPhoneValidator:
    """Validates Indian mobile phone numbers per the National Numbering Plan."""

    @staticmethod
    def clean(value: str) -> str:
        """Strip country code prefix, spaces, and dashes, leaving the 10-digit number."""
        digits = re.sub(r"\D", "", value)
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        elif len(digits) == 11 and digits.startswith("0"):
            digits = digits[1:]
        return digits

    def is_valid(self, value: str) -> bool:
        if not value:
            return False
        digits = self.clean(value)
        if len(digits) != 10:
            return False
        # Must start with 6, 7, 8, or 9
        return digits[0] in ("6", "7", "8", "9")

    def mask(self, value: str) -> str:
        """Mask mobile number: +91-XXXXX-43210."""
        digits = self.clean(value)
        if len(digits) != 10:
            return "+91-XXXXX-XXXXX"
        return f"+91-XXXXX-{digits[5:]}"

    def find_all(self, text: str) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for match in PHONE_REGEX.finditer(text):
            candidate = match.group(0).strip()
            if self.is_valid(candidate):
                results.append((candidate, self.mask(candidate)))
        return results
