"""Provider Dunia Games – kirim OTP via api.duniagames.co.id."""
from __future__ import annotations

import uuid
import requests
from provider.utils import fmt_plus, to_62, get_random_user_agent

API_URL = "https://api.duniagames.co.id/api/user/api/v2/user/send-otp"
REFERER = "https://duniagames.co.id/"


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via Dunia Games. Kembalikan True jika berhasil."""
    try:
        phone_plus = fmt_plus(mobile)
        phone_raw = to_62(mobile)
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://duniagames.co.id",
            "Referer": REFERER,
            "User-Agent": get_random_user_agent(),
            "x-device": str(uuid.uuid4()),
        }
        payload = {
            "phoneNumber": phone_plus,
            "userName": phone_raw,
        }
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        if resp.status_code in (200, 201):
            data = resp.json()
            status = data.get("status", {})
            return status.get("code") == 0 or "otp" in resp.text.lower()
        return False
    except Exception:
        return False

