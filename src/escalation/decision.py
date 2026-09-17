import re


# Intents that the system currently knows how to handle.
SUPPORTED_INTENTS = {
    "ios_update",
    "battery_charging",
    "app_issue",
    "device_performance",
    "connectivity",
    "hardware_display",
    "apple_id_account",
    "icloud_data",
    "media_services",
    "billing_payments",
}


def contains_any(text, patterns):
    """
    Return True if any regex pattern matches the text.
    """
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )


def decide_escalation(
    customer_message,
    predicted_intent,
    retrieved_cases,
):
    """
    Decide whether a customer request should be
    AUTO-HANDLE or ESCALATE.

    Returns:
        (decision, reason)
    """

    text = customer_message.lower()

    # ==================================================
    # 1. Unsupported / unknown intent
    # ==================================================

    if predicted_intent not in SUPPORTED_INTENTS:
        return (
            "ESCALATE",
            "The request does not clearly match a supported support intent."
        )

    # ==================================================
    # 2. No historical evidence
    # ==================================================

    if not retrieved_cases:
        return (
            "ESCALATE",
            "No sufficiently relevant historical support evidence was found."
        )

    # ==================================================
    # 3. Historical cases without support resolution
    # ==================================================

    has_support_response = any(
        case.get("support_messages")
        for case in retrieved_cases
    )

    if not has_support_response:
        return (
            "ESCALATE",
            "Relevant historical cases were found, but no usable support resolution was available."
        )

    # ==================================================
    # 4. Safety-critical situations
    # ==================================================

    if contains_any(
        text,
        [
            r"\bfire\b",
            r"\bsmoke\b",
            r"\bburn",
            r"\bexplod",
            r"\boverheat",
            r"\bhot\b",
            r"\bheat(?:ing)?\b",
            r"\bswollen\b",
            r"\bshock\b",
            r"\belectric\b",
            r"\bcatch(?:es|ed)? fire\b",
        ],
    ):
        return (
            "ESCALATE",
            "The message indicates a potential safety or hardware hazard."
        )

    # ==================================================
    # 5. Data loss / missing data
    # ==================================================

    if contains_any(
        text,
        [
            r"\blost photos?\b",
            r"\bphotos?\b.*\bmissing\b",
            r"\bphotos?\b.*\bdisappear",
            r"\blost everything\b",
            r"\blost all\b",
            r"\bdata loss\b",
            r"\bdata\b.*\bmissing\b",
            r"\btexts?\b.*\bdisappear",
            r"\btexts?\b.*\bmissing\b",
            r"\bmessages?\b.*\bdisappear",
            r"\bsongs?\b.*\bmissing\b",
            r"\bsongs?\b.*\blost\b",
        ],
    ):
        return (
            "ESCALATE",
            "The request involves potentially lost or missing user data."
        )

    # ==================================================
    # 6. Account access / authentication
    # ==================================================

    if contains_any(
        text,
        [
            r"\bfactory reset\b",
            r"\bcan't access\b",
            r"\bcannot access\b",
            r"\blocked out\b",
            r"\bcan't sign in\b",
            r"\bcannot sign in\b",
            r"\bcan't log in\b",
            r"\bcannot log in\b",
            r"\btwo[- ]factor\b",
            r"\b2fa\b",
            r"\bsign out\b.*\baccount\b",
            r"\bdelete account\b",
        ],
    ):
        return (
            "ESCALATE",
            "The request involves account access or authentication."
        )

    # ==================================================
    # 7. Repeated / recurring failures
    # ==================================================

    if contains_any(
        text,
        [
            r"\bkeeps? restarting\b",
            r"\bkeeps? rebooting\b",
            r"\brestarts? constantly\b",
            r"\brandomly restarts?\b",
            r"\bcrashes? constantly\b",
            r"\bkeeps? crashing\b",
            r"\bfreezes? constantly\b",
            r"\bkeeps? freezing\b",
            r"\bcan't stand it\b",
            r"\buntil it happens again\b",
            r"\bhappens again\b",
            r"\bmore often than not\b",
        ],
    ):
        return (
            "ESCALATE",
            "The issue is persistent or repeatedly recurring."
        )

    # ==================================================
    # 8. Explicit feature requests
    # ==================================================

    if contains_any(
        text,
        [
            r"\badd (?:a )?feature\b",
            r"\bplease add\b",
            r"\bcan you add\b",
            r"\bwould you add\b",
            r"\bneed (?:a )?feature\b",
            r"\bfeature request\b",
            r"\bneeds? .*notifications\b",
            r"\bdelivery report feature\b",
        ],
    ):
        return (
            "ESCALATE",
            "The customer is requesting a product feature rather than troubleshooting an existing supported issue."
        )

    # ==================================================
    # 9. Explicit request to fix / investigate behavior
    # ==================================================

    if contains_any(
        text,
        [
            r"\bwould you be able to fix\b",
            r"\bcan you fix\b",
            r"\bplease fix\b",
            r"\bis there anyway to fix\b",
            r"\bany way to fix\b",
            r"\bhow to fix\b",
            r"\bhow do you\b.*\biphone x\b",
            r"\bhow do i\b.*\biphone x\b",
            r"\bany ideas\b",
        ],
    ):
        return (
            "ESCALATE",
            "The customer is requesting case-specific investigation or troubleshooting."
        )

    # ==================================================
    # 10. Persistent problem indicators
    # ==================================================

    if contains_any(
        text,
        [
            r"\bconstantly\b",
            r"\bkeeps?\b",
            r"\bevery time\b",
            r"\bagain and again\b",
            r"\bstill\b",
            r"\bcontinues?\b",
            r"\brandomly\b",
            r"\bmultiple times\b",
            r"\b5 times\b",
        ],
    ):
        return (
            "ESCALATE",
            "The customer describes a persistent or recurring problem."
        )

    # ==================================================
    # 11. Multiple symptoms in one request
    # ==================================================

    symptom_patterns = [
        r"\bbattery\b",
        r"\bspeaker\b",
        r"\bscreen\b",
        r"\bcrash",
        r"\bglitch",
        r"\bfreez",
        r"\bcharging\b",
        r"\bwi[- ]?fi\b",
        r"\bheat(?:ing)?\b",
    ]

    symptom_count = sum(
        bool(re.search(pattern, text, re.IGNORECASE))
        for pattern in symptom_patterns
    )

    if symptom_count >= 2:
        return (
            "ESCALATE",
            "The request contains multiple symptoms and may require case-specific investigation."
        )

    # ==================================================
    # 12. Software update regression
    # ==================================================

    if contains_any(
        text,
        [
            r"\bafter updating\b",
            r"\bafter update\b",
            r"\bsince the update\b",
            r"\bsince updating\b",
            r"\bnew software update\b",
            r"\bios update\b",
            r"\bupdated ios\b",
            r"\bupdated my iphone\b",
            r"\bupdate\b.*\bcaused\b",
            r"\bupdate\b.*\bproblem\b",
            r"\bupdate\b.*\bbug",
            r"\bupdate\b.*\bglitch",
        ],
    ):
        if predicted_intent in {
            "ios_update",
            "battery_charging",
            "device_performance",
            "hardware_display",
            "app_issue",
            "connectivity",
        }:
            return (
                "ESCALATE",
                "The issue appears to be a regression associated with a software update."
            )

    # ==================================================
    # 13. Serious hardware malfunction
    # ==================================================

    if contains_any(
        text,
        [
            r"\bstopped charging\b",
            r"\bwon't turn on\b",
            r"\bdoesn't turn on\b",
            r"\bspeaker doesn't work\b",
            r"\bspeaker not working\b",
            r"\baudio jack\b",
            r"\baccessory may not be supported\b",
            r"\bcharger\b.*\bnot working\b",
        ],
    ):
        return (
            "ESCALATE",
            "The request describes a significant hardware or accessory malfunction."
        )

    # ==================================================
    # 14. Auto-handle
    # ==================================================

    return (
        "AUTO-HANDLE",
        "The request matches a supported intent and relevant historical support evidence was found."
    )