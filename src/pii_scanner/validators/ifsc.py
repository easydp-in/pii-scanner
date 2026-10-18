"""Indian Financial System Code (IFSC) validator and redactor."""

import re

# IFSC: 4 alphabetic chars (bank), 5th char is '0' (reserved), 6 alphanumeric (branch)
IFSC_REGEX = re.compile(r"\b([A-Z]{4})(0)([A-Z0-9]{6})\b", re.IGNORECASE)


class IFSCValidator:
    """Validates Indian bank branch IFSC codes."""

    def is_valid(self, value: str) -> bool:
        if not value:
            return False
        cleaned = value.strip().upper()
        return bool(IFSC_REGEX.fullmatch(cleaned))

    def mask(self, value: str) -> str:
        """Mask middle branch digits: SBIN0***234."""
        cleaned = value.strip().upper()
        if len(cleaned) != 11:
            return "XXXX0***XXX"
        return f"{cleaned[:5]}***{cleaned[8:]}"

    def find_all(self, text: str) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for match in IFSC_REGEX.finditer(text):
            candidate = match.group(0).upper()
            results.append((candidate, self.mask(candidate)))
        return results
