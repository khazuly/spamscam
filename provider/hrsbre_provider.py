"""Provider HRS-BRE – kirim OTP via career.hrs-bre.site."""
from __future__ import annotations

import random
import string
import requests
from provider.utils import fmt_08, generate_multipart, get_random_user_agent

BASE_URL = "https://career.hrs-bre.site"
SIGN_UP_PAGE = f"{BASE_URL}/auth/sign_up"
SIGN_UP_URL = f"{BASE_URL}/auth/sign_up_action"


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via HRS-BRE. Kembalikan True jika berhasil."""
    try:
        phone_08 = fmt_08(mobile)
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": BASE_URL,
            "Referer": SIGN_UP_PAGE,
        }
        session = requests.Session()
        r = session.get(SIGN_UP_PAGE, headers=headers, timeout=10)
        if r.status_code != 200:
            return False

        nik = "".join(random.choices(string.digits, k=16))
        email = "".join(random.choices(string.ascii_lowercase, k=8)) + "@gmail.com"
        username = "".join(random.choices(string.ascii_letters, k=8))
        password = "Aa1" + "".join(random.choices(string.ascii_letters + string.digits + "!@#$", k=7))
        boundary = "----WebKitFormBoundary" + "".join(random.choices(string.ascii_letters + string.digits, k=16))

        data = {
            "nik": nik,
            "email": email,
            "whatsapp": phone_08,
            "username": username,
            "password": password,
        }
        body = generate_multipart(data, boundary)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        resp = session.post(SIGN_UP_URL, headers=headers, data=body, timeout=15)
        if resp.status_code in (200, 201):
            return True
        text = resp.text.lower()
        return any(kw in text for kw in ["success", "berhasil", "otp", "verifikasi", "selamat"])
    except Exception:
        return False

