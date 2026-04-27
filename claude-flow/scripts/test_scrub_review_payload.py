from scrub_review_payload import scrub_text


def test_scrub_review_payload_redacts_common_secret_shapes():
    payload = """
Authorization: Bearer abc.def.ghi
OPENAI_API_KEY="sk-abcdefghijklmnopqrstuvwxyz1234"
password = "super-secret"
aws = AKIAABCDEFGHIJKLMNOP
"""

    scrubbed, redactions = scrub_text(payload)

    assert "abc.def.ghi" not in scrubbed
    assert "sk-abcdefghijklmnopqrstuvwxyz1234" not in scrubbed
    assert "super-secret" not in scrubbed
    assert "AKIAABCDEFGHIJKLMNOP" not in scrubbed
    assert redactions
    assert {item["rule"] for item in redactions} >= {
        "bearer_token",
        "assignment_secret",
        "aws_access_key",
    }
