"""Base classes, data models, and HTTP helpers for providers."""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Default connection and read timeout (seconds)
DEFAULT_TIMEOUT: tuple[float, float] = (5.0, 15.0)


@dataclass
class ProviderResult:
    """Hasil eksekusi permintaan OTP dari provider."""

    provider: str
    success: bool
    elapsed: float = 0.0
    message: str = ""

    def __bool__(self) -> bool:
        return self.success


def create_session(
    retries: int = 1,
    backoff_factor: float = 0.3,
    pool_connections: int = 10,
    pool_maxsize: int = 10,
) -> requests.Session:
    """Buat requests.Session dengan pool koneksi dan retry adapter bawaan."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
