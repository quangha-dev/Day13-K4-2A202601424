from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "passport": r"(?<!req-)(?<![A-Za-z0-9])(?i:[A-Z]\d{7,8})(?![A-Za-z0-9])",
    "address_vi": (
        r"(?i:\b(?:số\s+\d+[A-Za-z]?(?:[/-]\d+[A-Za-z]?)?\s*,?\s*)?"
        r"(?:đường|phố|phường|xã|quận|huyện|thành\s+phố|tỉnh)"
        r"\s+[\wÀ-ỹ][\wÀ-ỹ ./-]{0,60})"
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
