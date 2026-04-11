"""Test for lesson 03 — tu primer script en Python.

Runs curriculum/saludo.py with no args and with an argument, and
verifies the output in both cases.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPT = CURRICULUM_DIR / "saludo.py"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_exists() -> bool:
    if not SCRIPT.exists():
        print(f"  {FAIL} no existe curriculum/saludo.py")
        print(f"    {DIM}pista: crea el archivo con nano o VS Code{RST}")
        return False
    print(f"  {OK} saludo.py existe")
    return True


def run_script(*args: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc.returncode, proc.stdout.strip()


def check_no_args() -> bool:
    try:
        code, out = run_script()
    except subprocess.TimeoutExpired:
        print(f"  {FAIL} el script tardó demasiado — ¿está esperando input?")
        return False
    if code != 0:
        print(f"  {FAIL} el script falló al ejecutar sin argumentos (exit={code})")
        return False
    if out == "Hola, mundo!":
        print(f"  {OK} sin argumentos imprime: Hola, mundo!")
        return True
    print(f"  {FAIL} sin argumentos no imprime lo que esperaba")
    print(f"    {DIM}encontré: {out!r}{RST}")
    print(f"    {DIM}esperaba: 'Hola, mundo!'{RST}")
    return False


def check_with_arg() -> bool:
    try:
        code, out = run_script("Ana")
    except subprocess.TimeoutExpired:
        print(f"  {FAIL} el script tardó demasiado")
        return False
    if code != 0:
        print(f"  {FAIL} el script falló con argumento 'Ana' (exit={code})")
        return False
    if out == "Hola, Ana!":
        print(f"  {OK} con argumento 'Ana' imprime: Hola, Ana!")
        return True
    print(f"  {FAIL} con argumento 'Ana' no imprime lo que esperaba")
    print(f"    {DIM}encontré: {out!r}{RST}")
    print(f"    {DIM}esperaba: 'Hola, Ana!'{RST}")
    return False


def check_second_name() -> bool:
    try:
        code, out = run_script("Luis")
    except subprocess.TimeoutExpired:
        return False
    if code == 0 and out == "Hola, Luis!":
        print(f"  {OK} con argumento 'Luis' imprime: Hola, Luis!")
        return True
    print(f"  {FAIL} con argumento 'Luis' no imprime lo esperado")
    print(f"    {DIM}encontré: {out!r}{RST}")
    return False


def main() -> int:
    if not check_exists():
        return 1
    results = [
        check_no_args(),
        check_with_arg(),
        check_second_name(),
    ]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
