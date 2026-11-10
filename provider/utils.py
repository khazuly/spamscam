"""Utility functions and helpers for providers."""
from __future__ import annotations

import random
import re
from typing import Any

import requests

USER_AGENTS: list[str] = [
    # Chrome Android
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-S908E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-M315F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    # Chrome Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Safari iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
]


__all__ = [
    "USER_AGENTS",
    "to_62",
    "fmt_08",
    "fmt_nocode",
    "fmt_plus",
    "fmt_phone_only",
    "get_random_user_agent",
    "get_public_ip",
    "extract_csrf",
    "generate_multipart",
    "send_json_target",
]


def to_62(phone: str) -> str:
    """Normalisasi nomor telepon ke format 62."""
    n = phone.strip().replace(" ", "").replace("-", "").replace("+", "")
    if n.startswith("08"):
        return "62" + n[1:]
    if n.startswith("8"):
        return "62" + n
    if n.startswith("62"):
        return n
    return n


def fmt_08(phone: str) -> str:
    """Format nomor telepon ke 08..."""
    n = to_62(phone)
    return "0" + n[2:] if n.startswith("62") else n


def fmt_nocode(phone: str) -> str:
    """Format nomor tanpa kode negara (8...)."""
    n = to_62(phone)
    return n[2:] if n.startswith("62") else n


def fmt_plus(phone: str) -> str:
    """Format nomor telepon ke +62..."""
    n = to_62(phone)
    return "+" + n if not n.startswith("+") else n


def fmt_phone_only(phone: str) -> str:
    """Format nomor telepon tanpa kode (8...)."""
    return fmt_nocode(phone)


def get_random_user_agent() -> str:
    """Ambil user agent secara acak."""
    return random.choice(USER_AGENTS)


def get_public_ip() -> str:
    """Dapatkan IP publik via ipify."""
    try:
        return requests.get("https://api.ipify.org", timeout=5).text.strip()
    except Exception:
        return "127.0.0.1"


def extract_csrf(html: str) -> str | None:
    """Ekstrak CSRF token dari HTML."""
    patterns = [
        r'<meta\s+name="csrf-token"\s+content="([^"]+)"',
        r'<meta\s+name="csrf_token"\s+content="([^"]+)"',
        r'<input\s+type="hidden"\s+name="_token"\s+value="([^"]+)"',
        r'<input\s+type="hidden"\s+name="csrf_token"\s+value="([^"]+)"',
        r'<input\s+type="hidden"\s+name="_csrf"\s+value="([^"]+)"',
        r'csrf_token\s*=\s*"([^"]+)"',
    ]
    for p in patterns:
        m = re.search(p, html, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def generate_multipart(data: dict[str, Any], boundary: str) -> str:
    """Generate multipart form data string."""
    body = ""
    for key, val in data.items():
        body += f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
        body += f"{val}\r\n"
    body += f"--{boundary}--\r\n"
    return body


def send_json_target(
    url: str,
    payload_str: str,
    headers: dict[str, str],
    referer: str = "",
    success_keywords: list[str] | None = None,
    timeout: float = 15.0,
) -> bool:
    """Eksekusi request generic JSON ke endpoint target."""
    try:
        session = requests.Session()
        req_headers = dict(headers)
        if "User-Agent" not in req_headers:
            req_headers["User-Agent"] = get_random_user_agent()

        if referer:
            try:
                session.get(referer, headers={"User-Agent": req_headers["User-Agent"]}, timeout=8)
            except Exception:
                pass

        resp = session.post(url, headers=req_headers, data=payload_str, timeout=timeout)
        if resp.status_code in (200, 201, 202):
            return True

        if success_keywords:
            text = resp.text.lower()
            if any(kw.lower() in text for kw in success_keywords):
                return True

        return False
    except Exception:
        return False

