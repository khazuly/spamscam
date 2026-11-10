"""Provider Bonus Belanja – kirim OTP via bonusbelanja.com."""
from __future__ import annotations

import time
import requests
from requests.sessions import Session

from provider.base import DEFAULT_TIMEOUT, ProviderResult, create_session
from provider.utils import to_62, get_random_user_agent

API_URL = "https://www.bonusbelanja.com/api/auth/registration/app"
REFERER = "https://www.bonusbelanja.com/register/"


def send_otp_detailed(mobile: str, session: Session | None = None) -> ProviderResult:
    """Kirim OTP ke *mobile* via Bonus Belanja dengan informasi durasi dan status."""
    t0 = time.perf_counter()
    sess = session or create_session()
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
        resp = sess.post(API_URL, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        elapsed = time.perf_counter() - t0
        if resp.status_code in (200, 201):
            try:
                data = resp.json()
                is_ok = data.get("error") is False or "data" in data
                msg = "Berhasil" if is_ok else str(data.get("message") or "Gagal")
            except Exception:
                is_ok = True
                msg = "Berhasil"
            return ProviderResult(
                provider="Bonus Belanja",
                success=is_ok,
                elapsed=elapsed,
                message=msg,
            )
        return ProviderResult(
            provider="Bonus Belanja",
            success=False,
            elapsed=elapsed,
            message=f"HTTP {resp.status_code}",
        )
    except Exception as exc:  # pylint: disable=broad-except
        return ProviderResult(
            provider="Bonus Belanja",
            success=False,
            elapsed=time.perf_counter() - t0,
            message=str(exc),
        )


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via Bonus Belanja. Kembalikan True jika berhasil."""
    return send_otp_detailed(mobile).success
