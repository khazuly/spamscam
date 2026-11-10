# Provider package – ekspor fungsi send_otp dari setiap provider.
from provider.adakami_provider import (
    send_otp as adakami_send_otp,
    send_otp_detailed as adakami_send_otp_detailed,
)
from provider.indosaku_provider import (
    send_otp as indosaku_send_otp,
    send_otp_detailed as indosaku_send_otp_detailed,
)
from provider.kredione_provider import (
    send_otp as kredione_send_otp,
    send_otp_detailed as kredione_send_otp_detailed,
)
from provider.kreditnavigator_provider import (
    send_otp as kreditnavigator_send_otp,
    send_otp_detailed as kreditnavigator_send_otp_detailed,
)
from provider.rc_provider import (
    send_otp as rc_send_otp,
    send_otp_detailed as rc_send_otp_detailed,
)
from provider.hrsbre_provider import (
    send_otp as hrsbre_send_otp,
    send_otp_detailed as hrsbre_send_otp_detailed,
)
from provider.duniagames_provider import (
    send_otp as duniagames_send_otp,
    send_otp_detailed as duniagames_send_otp_detailed,
)
from provider.bonusbelanja_provider import (
    send_otp as bonusbelanja_send_otp,
    send_otp_detailed as bonusbelanja_send_otp_detailed,
)
from provider.base import ProviderResult, create_session, DEFAULT_TIMEOUT

PROVIDERS_REGISTRY: list[tuple[str, object]] = [
    ("AdaKami", adakami_send_otp_detailed),
    ("Indosaku", indosaku_send_otp_detailed),
    ("KrediOne", kredione_send_otp_detailed),
    ("RupiahCepat", rc_send_otp_detailed),
    ("KreditNavigator", kreditnavigator_send_otp_detailed),
    ("HRS-BRE", hrsbre_send_otp_detailed),
    ("Dunia Games", duniagames_send_otp_detailed),
    ("Bonus Belanja", bonusbelanja_send_otp_detailed),
]

__all__ = [
    "adakami_send_otp",
    "adakami_send_otp_detailed",
    "indosaku_send_otp",
    "indosaku_send_otp_detailed",
    "kredione_send_otp",
    "kredione_send_otp_detailed",
    "rc_send_otp",
    "rc_send_otp_detailed",
    "kreditnavigator_send_otp",
    "kreditnavigator_send_otp_detailed",
    "hrsbre_send_otp",
    "hrsbre_send_otp_detailed",
    "duniagames_send_otp",
    "duniagames_send_otp_detailed",
    "bonusbelanja_send_otp",
    "bonusbelanja_send_otp_detailed",
    "ProviderResult",
    "create_session",
    "DEFAULT_TIMEOUT",
    "PROVIDERS_REGISTRY",
]
