"""Provider Dunia Games – kirim OTP via api.duniagames.co.id."""
from __future__ import annotations

import time
import uuid
import requests
from requests.sessions import Session

from provider.base import DEFAULT_TIMEOUT, ProviderResult, create_session
from provider.utils import fmt_plus, to_62, get_random_user_agent

API_URL = "https://api.duniagames.co.id/api/user/api/v2/user/send-otp"
REFERER = "https://duniagames.co.id/"


def send_otp_detailed(mobile: str, session: Session | None = None) -> ProviderResult:
    """Kirim OTP ke *mobile* via Dunia Games dengan informasi durasi dan status."""
    t0 = time.perf_counter()
    sess = session or create_session()
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
        resp = sess.post(API_URL, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        elapsed = time.perf_counter() - t0
        if resp.status_code in (200, 201):
            try:
                data = resp.json()
                status = data.get("status", {})
                is_ok = status.get("code") == 0 or "otp" in resp.text.lower()
                msg = status.get("message") or ("Berhasil" if is_ok else "Gagal")
            except Exception:
                is_ok = True
                msg = "Berhasil"
            return ProviderResult(
                provider="Dunia Games",
                success=is_ok,
                elapsed=elapsed,
                message=str(msg),
            )
        return ProviderResult(
            provider="Dunia Games",
            success=False,
            elapsed=elapsed,
            message=f"HTTP {resp.status_code}",
        )
    except Exception as exc:  # pylint: disable=broad-except
        return ProviderResult(
            provider="Dunia Games",
            success=False,
            elapsed=time.perf_counter() - t0,
            message=str(exc),
        )


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via Dunia Games. Kembalikan True jika berhasil."""
    return send_otp_detailed(mobile).success
