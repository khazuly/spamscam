"""Provider RupiahCepat – kirim OTP via API terenkripsi AES-CBC."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import warnings
from typing import Any
from urllib.parse import quote, unquote

warnings.filterwarnings(
    "ignore",
    message="Unable to find acceptable character detection dependency",
)

try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad, unpad
except ImportError:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
from requests.sessions import Session

from provider.base import DEFAULT_TIMEOUT, ProviderResult, create_session

BASE = "https://apiservice.rupiahcepatweb.com"
USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
)

AES_KEY = "889511be9163d0d23997851e61033282"
AES_IV = "ec1d0eafaa9bbc096dfe255c86db9905"
_AES_KEY_BYTES = bytes.fromhex(AES_KEY)
_AES_IV_BYTES = bytes.fromhex(AES_IV)

SALT = "&97dab6b088ad"

OTP_CHANNEL = "2"

_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://h5.rupiahcepat.co.id",
    "Referer": "https://h5.rupiahcepat.co.id/",
    "User-Agent": USER_AGENT,
    "x-app-version-code": "999",
    "x-platform": "h5-whatsapp",
}


def _new_uuid() -> str:
    stamp = str(int(time.time() * 1000))
    return stamp + os.urandom(6).hex()


def _base_params(uuid: str) -> dict[str, Any]:
    now = str(int(time.time() * 1000))
    return {
        "access_token": "",
        "city": "",
        "app_free_memory": "",
        "longitude": "0",
        "total_boot_time_wake": "",
        "ui_version": "",
        "noise": "",
        "battery_max": "",
        "app_avaliable_memory": "",
        "app_version": "9.9.9",
        "app_version_code": "999",
        "version_code": "999",
        "platform": "h5",
        "app_max_memory": "",
        "brand": "",
        "manufacturer": "",
        "mem": "",
        "tz": "",
        "total_boot_time": "",
        "lat": "0",
        "latitude": "0",
        "is_sim": "0",
        "is_simulator": "0",
        "lon": "0",
        "is_tt": "0",
        "time_zone": "",
        "cpu_num": "",
        "product": "",
        "device": "",
        "is_google_service": "0",
        "battery_level": "0.7",
        "uuid": uuid,
        "request_time": now,
        "uptime": now,
        "rcid": uuid,
        "net": "other",
        "model": "",
        "width": "412",
        "network": "other",
        "height": "915",
        "os": "other",
    }


class _RupiahCepatAuth:

    def __init__(self, session: Session | None = None):
        self.s = session or create_session()
        self.s.headers.update(_HEADERS)
        self.uuid = _new_uuid()

    def _encrypt(self, data: dict[str, Any]) -> str:
        merged = _base_params(self.uuid)
        merged.update({key: "" if value is None else value for key, value in data.items()})
        signed_keys = sorted(merged)[:20]
        raw = "&".join(f"{key}={merged[key]}" for key in signed_keys)
        merged["signature"] = hashlib.md5((raw + SALT).encode()).hexdigest()
        cipher = AES.new(_AES_KEY_BYTES, AES.MODE_CBC, _AES_IV_BYTES)
        body = json.dumps(merged, separators=(",", ":")).encode()
        blob = base64.b64encode(cipher.encrypt(pad(body, 16))).decode()
        return quote(blob, safe="")

    def _decrypt(self, blob: str) -> Any:
        cipher = AES.new(_AES_KEY_BYTES, AES.MODE_CBC, _AES_IV_BYTES)
        raw = cipher.decrypt(base64.b64decode(unquote(blob)))
        return json.loads(unpad(raw, 16).decode())

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        res = self.s.post(
            BASE + path,
            data="data=" + self._encrypt(data),
            timeout=DEFAULT_TIMEOUT,
        )
        res.raise_for_status()
        body = res.json()
        if not isinstance(body, dict):
            raise RuntimeError(f"respons tidak valid: {body}")
        if body.get("code") == 0 and body.get("data"):
            body["real"] = self._decrypt(body["data"])
        return body

    def send_otp(self, mobile: str, channel: str = OTP_CHANNEL) -> dict[str, Any]:
        return self._post(
            "/api/v2/request_auth_code",
            {
                "mobile": mobile,
                "sms_type": "8",
                "otp_channel": channel,
            },
        )


def send_otp_detailed(mobile: str, session: Session | None = None) -> ProviderResult:
    """Kirim OTP ke *mobile* via RupiahCepat dengan informasi durasi dan status."""
    t0 = time.perf_counter()
    try:
        auth = _RupiahCepatAuth(session=session)
        res = auth.send_otp(mobile)
        elapsed = time.perf_counter() - t0
        is_ok = res.get("code") == 0
        msg = res.get("message") or res.get("msg") or ("Berhasil" if is_ok else f"Code: {res.get('code')}")
        return ProviderResult(
            provider="RupiahCepat",
            success=is_ok,
            elapsed=elapsed,
            message=str(msg),
        )
    except Exception as exc:  # pylint: disable=broad-except
        return ProviderResult(
            provider="RupiahCepat",
            success=False,
            elapsed=time.perf_counter() - t0,
            message=str(exc),
        )


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via RupiahCepat. Kembalikan True jika berhasil."""
    return send_otp_detailed(mobile).success
