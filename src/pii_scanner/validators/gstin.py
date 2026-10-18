"""Indian GSTIN (Goods and Services Tax Identification Number) validator and redactor."""

import re

from pii_scanner.validators.pan import PANValidator

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHAR_TO_VAL = {c: i for i, c in enumerate(CHARS)}

# Valid Indian State / UT codes under GST
VALID_STATE_CODES = {
    f"{i:02d}"
    for i in list(range(1, 39))  # 01-37 + Ladakh (38)
} | {"97", "99"}  # 97=Other Territory, 99=Centre

GSTIN_REGEX = re.compile(
    r"\b([0-9]{2})([A-Z]{3}[PCHFATBLJG][A-Z][0-9]{4}[A-Z])([1-9A-Z])(Z)([0-9A-Z])\b",
    re.IGNORECASE,
)


def calculate_gstin_check_digit(prefix14: str) -> str:
    """Calculate the 15th Mod-36 check digit for a 14-character GSTIN prefix."""
    if len(prefix14) != 14:
        raise ValueError("GSTIN prefix must be exactly 14 characters")

    prefix14 = prefix14.upper()
    total = 0
    for i, char in enumerate(prefix14):
        val = CHAR_TO_VAL.get(char)
        if val is None:
            raise ValueError(f"Invalid character in GSTIN: {char}")

        factor = 1 if (i % 2 == 0) else 2
        product = val * factor
        quotient = product // 36
        remainder = product % 36
        total += quotient + remainder

    check_code = (36 - (total % 36)) % 36
    return CHARS[check_code]


class GSTINValidator:
    """Validates 15-character GSTINs using state rules, embedded PAN checks, and Mod-36 checksums."""

    def __init__(self) -> None:
        self.pan_validator = PANValidator()

    def is_valid(self, value: str) -> bool:
        """Validate if a string is a legitimate GSTIN."""
        if not value:
            return False
        cleaned = value.strip().upper()
        if len(cleaned) != 15:
            return False

        # State code check
        state_code = cleaned[:2]
        if state_code not in VALID_STATE_CODES:
            return False

        # Embedded PAN check
        embedded_pan = cleaned[2:12]
        if not self.pan_validator.is_valid(embedded_pan):
            return False

        # 14th character must be 'Z'
        if cleaned[13] != "Z":
            return False

        # 15th character Mod-36 checksum check
        expected_check = calculate_gstin_check_digit(cleaned[:14])
        return cleaned[14] == expected_check

    def mask(self, value: str) -> str:
        """Mask GSTIN protecting the taxpayer's embedded PAN: 29XXXXX1234X1Z5."""
        cleaned = value.strip().upper()
        if len(cleaned) != 15:
            return "00XXXXX0000X1ZX"
        state = cleaned[:2]
        masked_pan = self.pan_validator.mask(cleaned[2:12])
        suffix = cleaned[12:]
        return f"{state}{masked_pan}{suffix}"

    def find_all(self, text: str) -> list[tuple[str, str]]:
        """Find and validate all GSTIN numbers in text."""
        results: list[tuple[str, str]] = []
        for match in GSTIN_REGEX.finditer(text):
            candidate = match.group(0).upper()
            if self.is_valid(candidate):
                results.append((candidate, self.mask(candidate)))
        return results
