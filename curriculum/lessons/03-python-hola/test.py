"""Test for lesson 03 — seu primeiro script em Python.

Runs curriculum/saudacao.py with no args and with an argument, and
verifies the output in both cases.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPT = CURRICULUM_DIR / "saudacao.py"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_exists() -> bool:
    if not SCRIPT.exists():
        print(f"  {FAIL} curriculum/saudacao.py não existe")
        print(f"    {DIM}dica: crie o arquivo com nano ou VS Code{RST}")
        return False
    print(f"  {OK} saudacao.py existe")
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
        print(f"  {FAIL} o script demorou demais — ele está esperando input?")
        return False
    if code != 0:
        print(f"  {FAIL} o script falhou ao rodar sem argumentos (exit={code})")
        return False
    if out == "Olá, mundo!":
        print(f"  {OK} sem argumentos imprime: Olá, mundo!")
        return True
    print(f"  {FAIL} sem argumentos não imprime o que eu esperava")
    print(f"    {DIM}encontrei: {out!r}{RST}")
    print(f"    {DIM}esperava:  'Olá, mundo!'{RST}")
    return False


def check_with_arg() -> bool:
    try:
        code, out = run_script("Ana")
    except subprocess.TimeoutExpired:
        print(f"  {FAIL} o script demorou demais")
        return False
    if code != 0:
        print(f"  {FAIL} o script falhou com argumento 'Ana' (exit={code})")
        return False
    if out == "Olá, Ana!":
        print(f"  {OK} com argumento 'Ana' imprime: Olá, Ana!")
        return True
    print(f"  {FAIL} com argumento 'Ana' não imprime o que eu esperava")
    print(f"    {DIM}encontrei: {out!r}{RST}")
    print(f"    {DIM}esperava:  'Olá, Ana!'{RST}")
    return False


def check_second_name() -> bool:
    try:
        code, out = run_script("Luiz")
    except subprocess.TimeoutExpired:
        return False
    if code == 0 and out == "Olá, Luiz!":
        print(f"  {OK} com argumento 'Luiz' imprime: Olá, Luiz!")
        return True
    print(f"  {FAIL} com argumento 'Luiz' não imprime o esperado")
    print(f"    {DIM}encontrei: {out!r}{RST}")
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
