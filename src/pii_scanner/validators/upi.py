"""Unified Payments Interface (UPI) VPA handle validator and redactor."""

import re

# UPI regex with negative lookahead to prevent matching standard email addresses
UPI_REGEX = re.compile(r"\b([a-zA-Z0-9.\-_]{2,50})@([a-zA-Z0-9]{2,30})(?!\.[a-zA-Z0-9]{2,})\b")

# NPCI certified Banks and PSP handles in India
COMMON_UPI_HANDLES = {
    # Google Pay
    "okaxis",
    "okhdfcbank",
    "okicici",
    "oksbi",
    # PhonePe
    "ybl",
    "ibl",
    "axl",
    # Paytm
    "paytm",
    # BHIM / NPCI
    "upi",
    # Major Indian Banks & Neobanks
    "barodampay",
    "cnrb",
    "pnb",
    "boi",
    "federal",
    "indus",
    "kotak",
    "idfcbank",
    "aubank",
    "airtel",
    "jio",
    "icici",
    "sbi",
    "hdfcbank",
    "postbank",
    "axisbank",
    "unionbank",
    "freecharge",
    "mobikwik",
    "amazonpay",
    "cred",
    "jupiteraxis",
    "slice",
    "superyes",
    "fifederal",
    "naviaxis",
    "tapicici",
    "timecosmos",
    "allbank",
    "syndicate",
    "canara",
    "centralbank",
    "corp",
    "dbs",
    "denabank",
    "equitas",
    "fbl",
    "hsbc",
    "idbi",
    "indianbank",
    "iob",
    "kbl",
    "kvb",
    "lvb",
    "obc",
    "psb",
    "sc",
    "sib",
    "tmb",
    "uco",
    "vijayabank",
    "yesbank",
}

EMAIL_TLDS = {
    "com",
    "org",
    "net",
    "edu",
    "gov",
    "io",
    "in",
    "co",
    "ai",
    "app",
    "dev",
    "me",
    "xyz",
    "info",
    "biz",
    "live",
    "tech",
    "online",
    "site",
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

        handle = match.group(2)
        if handle in EMAIL_TLDS:
            return False

        # If it's a known NPCI PSP handle
        if handle in COMMON_UPI_HANDLES:
            return True

        # If handle contains banking or payment keywords
        if any(k in handle for k in ("bank", "pay", "upi")) or handle.startswith("ok"):
            return True

        # If username is an Indian 10-digit mobile number (e.g. 9876543210@customvpa)
        username = match.group(1)
        if re.fullmatch(r"[6-9]\d{9}", username):
            return True

        return False

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
