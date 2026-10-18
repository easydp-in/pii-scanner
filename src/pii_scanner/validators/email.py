"""Email address validator and redactor."""

import re

EMAIL_REGEX = re.compile(r"\b([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b")


class EmailValidator:
    """Validates and masks email addresses."""

    def is_valid(self, value: str) -> bool:
        if not value:
            return False
        cleaned = value.strip()
        if cleaned.count("@") != 1:
            return False
        user, domain = cleaned.split("@", 1)
        if (
            not user
            or not domain
            or "." not in domain
            or domain.startswith(".")
            or domain.endswith(".")
        ):
            return False
        return bool(EMAIL_REGEX.fullmatch(cleaned))

    def mask(self, value: str) -> str:
        """Mask email address: p***a@example.com."""
        cleaned = value.strip().lower()
        if "@" not in cleaned:
            return "u***r@domain.com"
        username, domain = cleaned.split("@", 1)
        if len(username) <= 2:
            masked_user = username[0] + "***"
        else:
            masked_user = f"{username[0]}***{username[-1]}"
        return f"{masked_user}@{domain}"

    def find_all(self, text: str) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for match in EMAIL_REGEX.finditer(text):
            candidate = match.group(0)
            if self.is_valid(candidate):
                results.append((candidate, self.mask(candidate)))
        return results
