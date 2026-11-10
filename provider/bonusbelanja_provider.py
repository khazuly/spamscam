"""Provider Bonus Belanja – kirim OTP via bonusbelanja.com."""
from __future__ import annotations

import requests
from provider.utils import to_62, get_random_user_agent

API_URL = "https://www.bonusbelanja.com/api/auth/registration/app"
REFERER = "https://www.bonusbelanja.com/register/"


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via Bonus Belanja. Kembalikan True jika berhasil."""
    try:
        phone_62 = to_62(mobile)
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://www.bonusbelanja.com",
            "Referer": REFERER,
            "User-Agent": get_random_user_agent(),
        }
        payload = {
            "phone": phone_62,
            "name": "User",
            "agreeTnc": True,
            "agreeContact": True,
        }
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        if resp.status_code in (200, 201):
            data = resp.json()
            return data.get("error") is False
        return False
    except Exception:
        return False

