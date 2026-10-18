"""Unified Payments Interface (UPI) VPA handle validator and redactor."""

import re

# Common UPI handles and generic VPA pattern
UPI_REGEX = re.compile(r"\b([a-zA-Z0-9.\-_]{2,50})@([a-zA-Z0-9]{2,30})\b")

# Common banks / PSP handles in India
COMMON_UPI_HANDLES = {
    "okaxis",
    "okhdfcbank",
    "okicici",
    "oksbi",
    "paytm",
    "ybl",
    "ibl",
    "upi",
    "axl",
    "apl",
    "barodampay",
    "cnrb",
    "pnb",
}


class UPIValidator:
    """Validates UPI Virtual Payment Addresses (VPAs)."""

    def is_valid(self, value: str) -> bool:
        if not value:
            return False
        cleaned = value.strip().lower()
        match = UPI_REGEX.fullmatch(cleaned)
        if not match:
            return False

        # Avoid matching standard emails as UPI VPAs
        handle = match.group(2)
        if handle in {"com", "org", "net", "edu", "gov", "io", "in", "co"}:
            return False

        return True

    def mask(self, value: str) -> str:
        """Mask username in VPA: j***e@okhdfcbank."""
        cleaned = value.strip().lower()
        if "@" not in cleaned:
            return "u***r@upi"
        username, handle = cleaned.split("@", 1)
        if len(username) <= 2:
            masked_user = username[0] + "***"
        else:
            masked_user = f"{username[0]}***{username[-1]}"
        return f"{masked_user}@{handle}"

    def find_all(self, text: str) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for match in UPI_REGEX.finditer(text):
            candidate = match.group(0).lower()
            if self.is_valid(candidate):
                results.append((candidate, self.mask(candidate)))
        return results
