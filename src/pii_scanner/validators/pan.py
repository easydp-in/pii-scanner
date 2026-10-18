"""Indian Permanent Account Number (PAN) validator and redactor."""

import re

PAN_REGEX = re.compile(r"\b([A-Z]{3})([PCHFATBLJG])([A-Z])(\d{4})([A-Z])\b", re.IGNORECASE)

PAN_ENTITY_TYPES: dict[str, str] = {
    "P": "Individual",
    "C": "Company",
    "H": "HUF (Hindu Undivided Family)",
    "F": "Firm / LLP",
    "A": "Association of Persons (AOP)",
    "T": "Trust",
    "B": "Body of Individuals (BOI)",
    "L": "Local Authority",
    "J": "Artificial Juridical Person",
    "G": "Government Agency",
}


class PANValidator:
    """Validates Indian PAN cards and classifies legal entity types."""

    def is_valid(self, value: str) -> bool:
        """Check if a string matches the statutory Indian PAN structure."""
        if not value or len(value.strip()) != 10:
            return False
        return bool(PAN_REGEX.fullmatch(value.strip()))

    def get_entity_type(self, value: str) -> str:
        """Extract the legal entity type from the 4th character of PAN."""
        cleaned = value.strip().upper()
        if not self.is_valid(cleaned):
            return "Unknown"
        return PAN_ENTITY_TYPES.get(cleaned[3], "Unknown")

    def mask(self, value: str) -> str:
        """Mask PAN per privacy guidelines: XXXXX1234F."""
        cleaned = value.strip().upper()
        if len(cleaned) != 10:
            return "XXXXX0000X"
        return f"XXXXX{cleaned[5:]}"

    def find_all(self, text: str) -> list[tuple[str, str, str]]:
        """Find and validate all PAN numbers in text.

        Returns:
            List of tuples: (matched_text, masked_text, entity_type)
        """
        results: list[tuple[str, str, str]] = []
        for match in PAN_REGEX.finditer(text):
            candidate = match.group(0).upper()
            entity_type = self.get_entity_type(candidate)
            results.append((candidate, self.mask(candidate), entity_type))
        return results
