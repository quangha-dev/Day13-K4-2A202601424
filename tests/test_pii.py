import pytest

from app.logging_config import scrub_event
from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


@pytest.mark.parametrize(
    ("raw_value", "marker"),
    [
        ("001234567890", "REDACTED_CCCD"),
        ("4111111111111111", "REDACTED_CREDIT_CARD"),
        ("4111 1111 1111 1111", "REDACTED_CREDIT_CARD"),
        ("4111-1111-1111-1111", "REDACTED_CREDIT_CARD"),
        ("B1234567", "REDACTED_PASSPORT"),
        ("b1234567", "REDACTED_PASSPORT"),
        ("123 Đường Nguyễn Trãi", "REDACTED_ADDRESS_VI"),
        ("Phường Bến Nghé", "REDACTED_ADDRESS_VI"),
        ("Quận 1", "REDACTED_ADDRESS_VI"),
    ],
)
def test_scrub_supported_pii(raw_value: str, marker: str) -> None:
    out = scrub_text(f"Thông tin: {raw_value}")

    assert raw_value not in out
    assert marker in out


def test_scrub_event_recursively_scrubs_all_string_values() -> None:
    event = {
        "event": "Contact student@vinuni.edu.vn",
        "top_level": "0901234567",
        "payload": {
            "identity": "001234567890",
            "contacts": ["B1234567", {"card": "4111-1111-1111-1111"}],
            "addresses": ("Phường Bến Nghé", "safe"),
        },
        "latency_ms": 123.45,
    }

    scrubbed = scrub_event(None, "info", event)

    assert scrubbed["event"] == "Contact [REDACTED_EMAIL]"
    assert scrubbed["top_level"] == "[REDACTED_PHONE_VN]"
    assert scrubbed["payload"]["identity"] == "[REDACTED_CCCD]"
    assert scrubbed["payload"]["contacts"] == [
        "[REDACTED_PASSPORT]",
        {"card": "[REDACTED_CREDIT_CARD]"},
    ]
    assert scrubbed["payload"]["addresses"] == (
        "[REDACTED_ADDRESS_VI]",
        "safe",
    )
    assert scrubbed["latency_ms"] == 123.45


@pytest.mark.parametrize(
    "technical_value",
    [
        "req-1a2b3c4d",
        "2026-08-11T10:15:30.123Z",
        "gpt-4o-mini",
        "trace-token-count-1234",
        "cost_usd=0.0012",
        "session-a1b2c3d4e5f6",
    ],
)
def test_scrubber_preserves_non_pii_technical_values(technical_value: str) -> None:
    assert scrub_text(technical_value) == technical_value


def test_scrubber_preserves_lowercase_correlation_id() -> None:
    correlation_id = "req-c7040763"

    assert scrub_text(correlation_id) == correlation_id
