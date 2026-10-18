"""Person Name validator and redactor for Indian identity contexts."""

from __future__ import annotations

import re

# Standard Indian and international salutations / titles
SALUTATION_NAME_REGEX = re.compile(
    r"\b(Mr\.?|Mrs\.?|Ms\.?|Miss|Dr\.?|Prof\.?|Shri\.?|Smt\.?|Master)\s+([A-Z][a-zA-Z'.]{1,25}(?:\s+[A-Z][a-zA-Z'.]{1,25}){1,3})\b"
)

# Explicit label prefixes in forms, contracts, and documents
NAME_LABEL_REGEX = re.compile(
    r"(?i:\b(?:Name|Full\s*Name|Customer\s*Name|Employee\s*Name|Candidate\s*Name|Applicant\s*Name|Patient\s*Name|Student\s*Name|Father'?s?\s*Name|Mother'?s?\s*Name|Spouse\s*Name|Nominee\s*Name|Contact\s*Person)[\s:-]+)([A-Z][a-zA-Z'.]{1,25}(?:\s+[A-Z][a-zA-Z'.]{1,25}){1,3})\b"
)

# Non-name stop words to eliminate false positives in document titles and tables
NON_NAME_WORDS = {
    "total",
    "average",
    "status",
    "company",
    "private",
    "limited",
    "pvt",
    "ltd",
    "department",
    "invoice",
    "receipt",
    "agreement",
    "contract",
    "statement",
    "report",
    "summary",
    "overview",
    "policy",
    "terms",
    "conditions",
    "privacy",
    "compliance",
    "document",
    "file",
    "folder",
    "download",
    "desktop",
    "table",
    "column",
    "row",
    "date",
    "time",
    "year",
    "month",
    "amount",
    "balance",
    "india",
    "state",
    "city",
    "street",
    "road",
    "block",
    "floor",
    "services",
    "solutions",
    "technologies",
    "tech",
    "bank",
    "account",
    "number",
    "id",
    "code",
    "password",
    "token",
    "key",
    "admin",
    "manager",
    "director",
    "executive",
    "officer",
    "engineer",
    "developer",
    "analyst",
    "true",
    "false",
    "null",
    "none",
    "na",
    "n/a",
    "yes",
    "no",
    "description",
    "details",
}


class PersonNameValidator:
    """Validates and masks full human names in text and tabular records."""

    def is_valid_name(self, candidate: str) -> bool:
        """Validate if a candidate string is likely a genuine human name."""
        cleaned = candidate.strip()
        if not cleaned or len(cleaned) < 3 or len(cleaned) > 70:
            return False

        # Must not contain digits or special symbols
        if re.search(r"[\d@#$%^&*()_+=\[\]{}|\\/<>~`]", cleaned):
            return False

        tokens = cleaned.split()
        if len(tokens) < 2 or len(tokens) > 4:
            return False

        for t in tokens:
            lower_t = t.lower().strip(".,'")
            if lower_t in NON_NAME_WORDS:
                return False
            if not re.match(r"^[A-Za-z'.]+$", t):
                return False
            # Each word must start with an uppercase letter
            if not t[0].isupper():
                return False

        return True

    def is_valid(self, text: str, is_column_name: bool = False) -> bool:
        """Validate if text represents a person name in context."""
        cleaned = text.strip()
        if is_column_name:
            return self.is_valid_name(cleaned)

        # Check salutations
        sal_match = SALUTATION_NAME_REGEX.fullmatch(cleaned)
        if sal_match and self.is_valid_name(sal_match.group(2)):
            return True

        # Check explicit labels
        label_match = NAME_LABEL_REGEX.fullmatch(cleaned)
        if label_match and self.is_valid_name(label_match.group(1)):
            return True

        return False

    def mask(self, name: str) -> str:
        """Mask person name safely: 'Ramesh Kumar' -> 'R***h K***r'."""
        cleaned = name.strip()
        prefix = ""

        # Check for label prefix like 'Name: ', 'Customer Name: '
        label_match = re.match(
            r"^((?i:(?:Name|Full\s*Name|Customer\s*Name|Employee\s*Name|Candidate\s*Name|Applicant\s*Name|Patient\s*Name|Student\s*Name|Father'?s?\s*Name|Mother'?s?\s*Name|Spouse\s*Name|Nominee\s*Name|Contact\s*Person))[\s:-]+)(.+)$",
            cleaned,
        )
        if label_match:
            prefix = label_match.group(1)
            cleaned = label_match.group(2).strip()

        for sal in (
            "Master",
            "Prof.",
            "Prof",
            "Miss",
            "Shri.",
            "Shri",
            "Smt.",
            "Smt",
            "Mrs.",
            "Mrs",
            "Mr.",
            "Mr",
            "Ms.",
            "Ms",
            "Dr.",
            "Dr",
        ):
            if cleaned.startswith(sal + " ") or cleaned.startswith(sal + "."):
                prefix += sal + " "
                cleaned = cleaned[len(sal) :].lstrip(". ")
                break

        parts = cleaned.split()
        masked_parts: list[str] = []
        for p in parts:
            if len(p) <= 2:
                masked_parts.append(p[0] + "*")
            else:
                masked_parts.append(f"{p[0]}***{p[-1]}")
        return prefix + " ".join(masked_parts)

    def find_all(self, text: str) -> list[tuple[str, str]]:
        """Find person names in unstructured text."""
        results: list[tuple[str, str]] = []
        seen: set[str] = set()

        # 1. Salutation-prefixed names (e.g. Mr. Rajesh Kumar, Dr. Priya Sharma)
        for match in SALUTATION_NAME_REGEX.finditer(text):
            full_match = match.group(0).strip()
            name_part = match.group(2).strip()
            if self.is_valid_name(name_part) and full_match not in seen:
                seen.add(full_match)
                results.append((full_match, self.mask(full_match)))

        # 2. Label-prefixed names (e.g. Employee Name: Amit Singh)
        for match in NAME_LABEL_REGEX.finditer(text):
            name_part = match.group(1).strip()
            if self.is_valid_name(name_part) and name_part not in seen:
                seen.add(name_part)
                results.append((name_part, self.mask(name_part)))

        return results
