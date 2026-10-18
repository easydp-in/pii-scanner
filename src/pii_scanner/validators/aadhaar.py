"""Aadhaar number validator and redactor conforming to UIDAI specifications."""

import re

from pii_scanner.validators.verhoeff import validate_verhoeff

# Aadhaar regex candidate finder: 12 digits, optional spaces or dashes, starting with 2-9
AADHAAR_CANDIDATE_REGEX = re.compile(r"\b([2-9]\d{3}[-\s]?\d{4}[-\s]?\d{4})\b")


class AadhaarValidator:
    """Validates Indian Aadhaar numbers using UIDAI formatting rules and Verhoeff checksum."""

    @staticmethod
    def clean(value: str) -> str:
        """Remove hyphens and whitespace."""
        return re.sub(r"[\s\-]", "", value)

    def is_valid(self, value: str) -> bool:
        """Check if a string is a valid Aadhaar number."""
        cleaned = self.clean(value)
        if len(cleaned) != 12 or not cleaned.isdigit():
            return False

        # UIDAI rules: Aadhaar numbers never start with 0 or 1
        if cleaned[0] in ("0", "1"):
            return False

        # Must pass Verhoeff dihedral checksum
        return validate_verhoeff(cleaned)

    def mask(self, value: str) -> str:
        """Mask Aadhaar number per UIDAI and DPDP guidelines: XXXX-XXXX-1234."""
        cleaned = self.clean(value)
        if len(cleaned) != 12:
            return "XXXX-XXXX-XXXX"
        return f"XXXX-XXXX-{cleaned[8:]}"

    def find_all(self, text: str) -> list[tuple[str, str]]:
        """Find and validate all Aadhaar numbers in text.

        Returns:
            List of tuples: (matched_text, masked_text)
        """
        results: list[tuple[str, str]] = []
        for match in AADHAAR_CANDIDATE_REGEX.finditer(text):
            candidate = match.group(1)
            if self.is_valid(candidate):
                results.append((candidate, self.mask(candidate)))
        return results
