# Provider package – ekspor fungsi send_otp dari setiap provider.
from provider.adakami_provider import send_otp as adakami_send_otp
from provider.indosaku_provider import send_otp as indosaku_send_otp
from provider.kredione_provider import send_otp as kredione_send_otp
from provider.rc_provider import send_otp as rc_send_otp
from provider.kreditnavigator_provider import send_otp as kreditnavigator_send_otp
from provider.hrsbre_provider import send_otp as hrsbre_send_otp
from provider.duniagames_provider import send_otp as duniagames_send_otp
from provider.bonusbelanja_provider import send_otp as bonusbelanja_send_otp

__all__ = [
    "adakami_send_otp",
    "indosaku_send_otp",
    "kredione_send_otp",
    "rc_send_otp",
    "kreditnavigator_send_otp",
    "hrsbre_send_otp",
    "duniagames_send_otp",
    "bonusbelanja_send_otp",
]
