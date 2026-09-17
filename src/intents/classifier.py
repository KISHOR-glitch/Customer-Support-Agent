import re


def has(text, *patterns):
    """
    Return True if any pattern matches the text.
    """
    return any(re.search(pattern, text) for pattern in patterns)


def predict_intent(text: str):
    text = text.lower()

    # --------------------------------------------------
    # 1. Apple ID / Account access
    # --------------------------------------------------
    # Account access takes priority over generic iCloud mentions.
    if has(
        text,
        r"\bfactory reset\b.*\bicloud\b",
        r"\bicloud\b.*\bfactory reset\b",
        r"\bget into icloud\b",
        r"\baccess icloud\b",
        r"\bcan't access\b",
        r"\bcannot access\b",
        r"\blocked out\b",
        r"\bsign ?in\b",
        r"\blog ?in\b",
        r"\bapple id\b",
        r"\bpassword\b",
    ):
        return "apple_id_account", 0.70

    # --------------------------------------------------
    # 2. Battery / Charging
    # --------------------------------------------------
    if has(
        text,
        r"\bbattery\b",
        r"\bdrain(?:ing|s)?\b",
        r"\bcharge(?:d|s|ing)?\b",
        r"\bcharging\b",
        r"\bstopped charging\b",
        r"\bwon't charge\b",
        r"\bshutdown\b",
        r"\bshut down\b",
        r"\bwithout battery\b",
    ):
        return "battery_charging", 0.70

    # --------------------------------------------------
    # 3. App Issues
    # --------------------------------------------------
    if has(
        text,
        r"\bapp\b.*\bcrash",
        r"\bapps\b.*\bcrash",
        r"\bcrash.*\bapp\b",
        r"\bcrash.*\bapps\b",
        r"\brunning any app\b",
    ):
        return "app_issue", 0.70

    # --------------------------------------------------
    # 4. Connectivity
    # --------------------------------------------------
    if has(
        text,
        r"\bwi[- ]?fi\b",
        r"\bbluetooth\b",
        r"\bgps\b",
        r"\bhotspot\b",
        r"\bcellular\b",
        r"\bsignal\b",
    ):
        return "connectivity", 0.70

    # --------------------------------------------------
    # 5. iCloud / Data
    # --------------------------------------------------
    if has(
        text,
        r"\bicloud\b",
        r"\bbackup\b",
        r"\bsync(?:ing)?\b",
        r"\bsynchroniz",
        r"\bphotos?\b.*\bmissing\b",
        r"\bphotos?\b.*\blost\b",
        r"\bdata\b.*\blost\b",
        r"\bdata\b.*\bmissing\b",
        r"\btexts?\b.*\bdisappear",
        r"\btexts?\b.*\bmissing\b",
        r"\bmessages?\b.*\bdisappear",
    ):
        return "icloud_data", 0.70

    # --------------------------------------------------
    # 6. Media Services
    # --------------------------------------------------
    if has(
        text,
        r"\bapple music\b",
        r"\bitunes\b",
        r"\bmusic\b",
        r"\bsong(s)?\b",
        r"\bmovie\b",
        r"\b4k\b",
        r"\bvideo\b",
        r"\bplayback\b",
        r"\bgarage ?band\b",
    ):
        return "media_services", 0.70

    # --------------------------------------------------
    # 7. Billing / Payments
    # --------------------------------------------------
    if has(
        text,
        r"\bapple pay\b",
        r"\bpayment\b",
        r"\bcharge(d)?\b",
        r"\bbilling\b",
        r"\brefund\b",
        r"\bprice\b",
        r"\bcurrency\b",
    ):
        return "billing_payments", 0.70

    # --------------------------------------------------
    # 8. Hardware / Display
    # --------------------------------------------------
    if has(
        text,
        r"\bscreen\b",
        r"\bdisplay\b",
        r"\bcamera\b",
        r"\bspeaker\b",
        r"\bheadphone(s)?\b",
        r"\bearpod(s)?\b",
        r"\baudio jack\b",
        r"\bcharger\b",
        r"\bcharging port\b",
        r"\bvibrat",
        r"\btouch id\b",
        r"\bhome button\b",
    ):
        return "hardware_display", 0.70

    # --------------------------------------------------
    # 9. Device Performance
    # --------------------------------------------------
    if has(
        text,
        r"\bslow\b",
        r"\bslower\b",
        r"\bfreez",
        r"\brestart",
        r"\breboot",
        r"\bstutter",
        r"\blag\b",
    ):
        return "device_performance", 0.70

    # --------------------------------------------------
    # 10. iOS / Software Update
    # --------------------------------------------------
    if has(
        text,
        r"\bios\s*\d",
        r"\bios\s+update\b",
        r"\bupdate\b.*\binstall\b",
        r"\binstall\b.*\bupdate\b",
        r"\bdownload\b.*\bios\b",
        r"\bupgrade\b",
        r"\bdowngrade\b",
        r"\bbeta\b",
        r"\bupdate\b.*\blatest ios\b",
        r"\blatest ios\b",
    ):
        return "ios_update", 0.70

    # --------------------------------------------------
    # 11. Other / Insufficient Information
    # --------------------------------------------------
    if has(
        text,
        r"\badd (?:a )?feature\b",
        r"\bplease add\b",
        r"\bcan you add\b",
        r"\bfeature\b.*\bplease\b",
        r"\bglitch\b",
        r"\bissue\b",
        r"\bproblem\b",
    ):
        return "other_insufficient_information", 0.20

    # Default
    return "other_insufficient_information", 0.20