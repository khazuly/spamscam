"""Provider AdaKami – kirim OTP via slider CAPTCHA."""
from __future__ import annotations

import base64
import time
import uuid
import warnings
from typing import Any

warnings.filterwarnings(
    "ignore",
    message="Unable to find acceptable character detection dependency",
)

from requests.sessions import Session

from provider.base import DEFAULT_TIMEOUT, ProviderResult, create_session

try:
    import numpy as np
    import cv2
except ImportError:
    np = None  # type: ignore[assignment]
    cv2 = None  # type: ignore[assignment]

BASE = "https://h5.adakami.id"
LANDING_REFERER = f"{BASE}/landing/register?id=64&skin=newUI&needAbTest=false"

slider_endpoint = f"{BASE}/gateway/h5anon/merchantwook/verify/verificationCode/slider"
api_endpoint = f"{BASE}/gateway/h5anon/merchantwook/user/registerOrLogin/sendOtp"

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
)


def _get_headers() -> dict[str, str]:
    return {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "X-ADA-OS": "android",
        "X-CLIENT": "h5",
        "merchant-no": "PA_WOOK_ADA",
        "deviceId": uuid.uuid4().hex,
        "appId": "800006",
        "platform": "h5_PA_WOOK_ADA",
        "tenantId": "1",
        "product": "H5_WOOK",
        "Origin": BASE,
        "Referer": LANDING_REFERER,
        "User-Agent": USER_AGENT,
    }


def _new_session() -> Session:
    s = create_session()
    s.headers.update(_get_headers())
    try:
        s.get(LANDING_REFERER, timeout=DEFAULT_TIMEOUT)
    except Exception:
        pass
    return s


def _b64_to_cv_image(value: str, flags: int) -> np.ndarray:
    if cv2 is None or np is None:
        raise RuntimeError("OpenCV (cv2) atau numpy belum terinstall")
    raw = base64.b64decode(value)
    return cv2.imdecode(np.frombuffer(raw, np.uint8), flags)


def _solve_slider_x(challenge: dict) -> float:
    """Temukan posisi X slider menggunakan template matching teroptimasi."""
    if cv2 is None:
        raise RuntimeError("OpenCV tidak tersedia")

    original = _b64_to_cv_image(challenge["originalImage"], cv2.IMREAD_COLOR)
    piece = _b64_to_cv_image(challenge["slidingImage"], cv2.IMREAD_UNCHANGED)

    mask = piece[:, :, 3] if piece.shape[2] == 4 else None
    template = piece[:, :, :3]

    h_img = original.shape[0]
    h_tpl = template.shape[0]
    w_img = original.shape[1]

    # Optimasi: Potong vertikal original hanya di sekitar targetYHeightPercent
    expected_y = round(float(challenge.get("targetYHeightPercent", 0.5)) * h_img)
    lo = max(0, expected_y - 4)
    hi = min(h_img - h_tpl, expected_y + 4)
    if hi < lo:
        lo, hi = 0, max(0, h_img - h_tpl)

    crop_y_end = min(h_img, hi + h_tpl)
    cropped_original = original[lo:crop_y_end, :]

    result = cv2.matchTemplate(
        cropped_original, template, cv2.TM_SQDIFF_NORMED, mask=mask
    )

    _, _, min_loc, _ = cv2.minMaxLoc(result)
    return float(min_loc[0] / w_img)


class _AdakamiAuth:

    def __init__(self, session: Session | None = None):
        self.s = session or _new_session()

    def _post(self, url: str, payload: dict) -> dict:
        r = self.s.post(url, json=payload, headers=_get_headers(), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def _slider_challenge(self, mobile: str) -> dict:
        res = self._post(slider_endpoint, {"mobile": mobile})
        if res.get("result") != 0:
            msg = res.get("resultMessage") or f"Slider ditolak: kode {res.get('result')}"
            raise RuntimeError(msg)
        content = res.get("content")
        if not isinstance(content, dict):
            raise RuntimeError("Konten slider tidak valid")
        return content

    def send_otp(self, mobile: str, max_attempts: int = 3) -> dict:
        last: dict = {}
        for _ in range(max_attempts):
            challenge = self._slider_challenge(mobile)
            # Gunakan targetXWidthPercent bawaan server atau template matcher
            x_width = challenge.get("targetXWidthPercent")
            if (x_width is None or x_width <= 0) and cv2 is not None:
                x_width = _solve_slider_x(challenge)

            payload = {
                "xWidthPresent": x_width or 0.5,
                "mobile": mobile,
                "md5Mobile": "",
                "smsTypeEnum": "SMS",
            }
            last = self._post(api_endpoint, payload)
            if last.get("result") == 0:
                return last
            if last.get("result") not in (-95, 101021):
                return last
        return last


def send_otp_detailed(mobile: str, session: Session | None = None) -> ProviderResult:
    """Kirim OTP ke *mobile* via AdaKami dengan informasi durasi dan status."""
    t0 = time.perf_counter()
    try:
        auth = _AdakamiAuth(session=session)
        res = auth.send_otp(mobile)
        elapsed = time.perf_counter() - t0
        is_ok = res.get("result") == 0
        msg = res.get("resultMessage") or res.get("message") or ("Berhasil" if is_ok else f"Result code: {res.get('result')}")
        return ProviderResult(
            provider="AdaKami",
            success=is_ok,
            elapsed=elapsed,
            message=str(msg),
        )
    except Exception as exc:  # pylint: disable=broad-except
        return ProviderResult(
            provider="AdaKami",
            success=False,
            elapsed=time.perf_counter() - t0,
            message=str(exc),
        )


def send_otp(mobile: str) -> bool:
    """Kirim OTP ke *mobile* via AdaKami. Kembalikan True jika berhasil."""
    return send_otp_detailed(mobile).success
