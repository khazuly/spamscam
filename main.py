from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import math
import re
import shutil
import sys
import time
from typing import Callable

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from provider import PROVIDERS_REGISTRY, ProviderResult

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

COOLDOWN_SECONDS = 62

_BLOCK_GLYPHS: dict[str, tuple[str, ...]] = {
    "S": ("███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"),
    "P": ("██████╗ ", "██╔══██╗", "██████╔╝", "██╔═══╝ ", "██║     ", "╚═╝     "),
    "A": (" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"),
    "M": ("███╗   ███╗", "████╗ ████║", "██╔████╔██║", "██║╚██╔╝██║", "██║ ╚═╝ ██║", "╚═╝     ╚═╝"),
    "C": (" ██████╗", "██╔════╝", "██║     ", "██║     ", "╚██████╗", " ╚═════╝"),
}
_WORD = "SPAMSCAM"

THEME = Theme(
    {
        "accent": "bold cyan",
        "muted": "dim",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
    }
)

console = Console(theme=THEME, highlight=False, color_system="standard")


def _term_width() -> int:
    return min(88, shutil.get_terminal_size((88, 24)).columns)


def _build_block_rows(word: str) -> list[Text]:
    rows: list[Text] = []
    for row in range(6):
        line = Text()
        for letter in word:
            for ch in _BLOCK_GLYPHS[letter][row]:
                line.append(ch, "bold white" if ch == "█" else "dim")
        rows.append(line)
    return rows


def print_banner() -> None:
    width = _term_width()
    console.print()
    sample = "".join(_BLOCK_GLYPHS[c][0] for c in _WORD)
    try:
        if len(sample) <= width:
            for row in _build_block_rows(_WORD):
                console.print(row, width=width)
        else:
            console.print("SPAMSCAM", style="bold white")
    except Exception:
        console.print("SPAMSCAM", style="bold white")
    console.print()
    console.print("SPAMSCAM / OTP SPAM TOOL (OPTIMIZED)", style="bold")
    console.print("Concurrent multi-provider · High-performance cycle · Auto cooldown", style="muted")
    console.print()


def normalize_phone(value: str) -> str:
    """Bersihkan format nomor HP ke format standar 08xxxxxxxx."""
    value = re.sub(r"\D", "", value)
    if value.startswith("62"):
        value = "0" + value[2:]
    return value


def countdown(seconds: float) -> None:
    end = time.monotonic() + seconds
    while True:
        remaining = end - time.monotonic()
        if remaining <= 0:
            break
        mins, secs = divmod(math.ceil(remaining), 60)
        print(f"\r  Cooldown: {mins:02d}:{secs:02d} ...", end="", flush=True)
        time.sleep(min(0.5, remaining))
    print("\r" + " " * 30 + "\r", end="", flush=True)


def read_input() -> tuple[str, int] | None:
    try:
        raw_hp = input("  Nomor HP      : ").strip()
        no_hp = normalize_phone(raw_hp)

        if not re.fullmatch(r"08\d{8,13}", no_hp):
            console.print("\n  [!] Nomor HP tidak valid. Contoh: 08978397772\n", style="error")
            return None

        raw = input("  Jumlah resend : ").strip()
        try:
            jml_resend = int(raw) if raw else 0
        except ValueError:
            console.print("\n  [!] Jumlah resend harus berupa angka.\n", style="error")
            return None

        if jml_resend < 1:
            console.print("\n  [!] Jumlah resend minimal 1.\n", style="error")
            return None

        return no_hp, jml_resend
    except (KeyboardInterrupt, EOFError):
        console.print("\n  [!] Input dibatalkan.\n", style="warning")
        return None


def run_cycle_parallel(
    no_hp: str,
    cycle: int,
    total: int,
    providers: list[tuple[str, Callable[..., ProviderResult]]],
    max_workers: int = 5,
) -> list[ProviderResult]:
    """Jalankan permintaan OTP ke seluruh provider secara konkuren / paralel."""
    width = _term_width()
    divider = "─" * min(60, width - 2)

    console.print()
    console.print(f"  {divider}", style="muted")
    header = Text()
    header.append(f"  Siklus {cycle}/{total}", style="accent")
    header.append(f"  ·  Target: {no_hp}", style="muted")
    header.append(f"  ·  Mode: Paralel ({min(max_workers, len(providers))} workers)", style="muted")
    console.print(header)
    console.print(f"  {divider}", style="muted")

    results: list[ProviderResult] = []
    col_w = 30

    with ThreadPoolExecutor(max_workers=min(max_workers, len(providers))) as executor:
        future_map = {
            executor.submit(fn, no_hp): name
            for name, fn in providers
        }

        for future in as_completed(future_map):
            name = future_map[future]
            label = f"  [{name}]"
            try:
                res = future.result()
                results.append(res)
                status_text = "[ [success]OK[/success] ]" if res.success else "[ [error]Gagal[/error] ]"
                duration_text = f"({res.elapsed:.2f}s)"
                extra = f" - {res.message[:30]}" if (not res.success and res.message) else ""
                console.print(f"{label:{col_w}} {status_text} {duration_text}{extra}")
            except Exception as exc:  # pylint: disable=broad-except
                fail_res = ProviderResult(provider=name, success=False, message=str(exc))
                results.append(fail_res)
                console.print(f"{label:{col_w}} [ [error]Error[/error] ] ({str(exc)[:35]})")

    console.print(f"  {divider}", style="muted")
    return results


def run_cycle_sequential(
    no_hp: str,
    cycle: int,
    total: int,
    providers: list[tuple[str, Callable[..., ProviderResult]]],
) -> list[ProviderResult]:
    """Jalankan permintaan OTP secara sekuensial (fallback)."""
    width = _term_width()
    divider = "─" * min(60, width - 2)

    console.print()
    console.print(f"  {divider}", style="muted")
    header = Text()
    header.append(f"  Siklus {cycle}/{total}", style="accent")
    header.append(f"  ·  Target: {no_hp}", style="muted")
    header.append("  ·  Mode: Sekuensial", style="muted")
    console.print(header)
    console.print(f"  {divider}", style="muted")

    results: list[ProviderResult] = []
    col_w = 30

    for name, send_fn in providers:
        label = f"  [{name}]"
        print(f"{label:{col_w}}", end="", flush=True)

        try:
            res = send_fn(no_hp)
            results.append(res)
            if res.success:
                console.print(f"[ [success]OK[/success] ] ({res.elapsed:.2f}s)")
            else:
                extra = f" - {res.message[:30]}" if res.message else ""
                console.print(f"[ [error]Gagal[/error] ] ({res.elapsed:.2f}s){extra}")
        except Exception as exc:  # pylint: disable=broad-except
            fail_res = ProviderResult(provider=name, success=False, message=str(exc))
            results.append(fail_res)
            console.print(f"[ [error]Error[/error] ] ({str(exc)[:35]})")

    console.print(f"  {divider}", style="muted")
    return results


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SpamScam - High Performance Multi-Provider OTP Testing Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", "--phone", type=str, help="Nomor HP target (format: 08xxxxxxxx)")
    parser.add_argument("-c", "--count", type=int, default=None, help="Jumlah siklus pengiriman")
    parser.add_argument("-d", "--cooldown", type=int, default=COOLDOWN_SECONDS, help="Cooldown antar-siklus (detik)")
    parser.add_argument("-w", "--workers", type=int, default=5, help="Jumlah paralel worker thread")
    parser.add_argument("--providers", type=str, default=None, help="Daftar provider (pisahkan dengan koma)")
    parser.add_argument("--sequential", action="store_true", help="Gunakan mode sekuensial alih-alih paralel")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    print_banner()

    # Filter provider jika ditentukan
    active_providers = list(PROVIDERS_REGISTRY)
    if args.providers:
        selected = {p.strip().lower() for p in args.providers.split(",") if p.strip()}
        active_providers = [p for p in active_providers if p[0].lower() in selected]
        if not active_providers:
            available = ", ".join(p[0] for p in PROVIDERS_REGISTRY)
            console.print(f"  [!] Provider tidak valid. Tersedia: {available}", style="error")
            return

    # Ambil nomor HP dan jumlah resend dari argumen CLI atau input interaktif
    if args.phone and args.count is not None:
        no_hp = normalize_phone(args.phone)
        if not re.fullmatch(r"08\d{8,13}", no_hp):
            console.print("\n  [!] Nomor HP tidak valid. Contoh: 08978397772\n", style="error")
            return
        if args.count < 1:
            console.print("\n  [!] Jumlah resend minimal 1.\n", style="error")
            return
        jml_resend = args.count
    else:
        data = read_input()
        if data is None:
            return
        no_hp, jml_resend = data

    cooldown_secs = max(0, args.cooldown)
    all_results: list[ProviderResult] = []
    start_total = time.perf_counter()

    try:
        for i in range(1, jml_resend + 1):
            if args.sequential:
                cycle_results = run_cycle_sequential(no_hp, i, jml_resend, active_providers)
            else:
                cycle_results = run_cycle_parallel(
                    no_hp, i, jml_resend, active_providers, max_workers=args.workers
                )

            all_results.extend(cycle_results)

            if i < jml_resend and cooldown_secs > 0:
                console.print(
                    f"\n  Cooldown {cooldown_secs} detik sebelum siklus berikutnya...",
                    style="muted",
                )
                countdown(cooldown_secs)

    except KeyboardInterrupt:
        console.print("\n\n  [!] Dibatalkan oleh pengguna.\n", style="warning")
    finally:
        total_time = time.perf_counter() - start_total
        if all_results:
            total_req = len(all_results)
            total_ok = sum(1 for r in all_results if r.success)
            total_fail = total_req - total_ok

            console.print("\n  [ringkasan]", style="accent")
            console.print(f"  Total Permintaan : {total_req}")
            console.print(f"  Berhasil         : [success]{total_ok}[/success]")
            console.print(f"  Gagal            : [error]{total_fail}[/error]")
            console.print(f"  Durasi Total     : {total_time:.2f}s\n")
        else:
            console.print()


if __name__ == "__main__":
    main()
