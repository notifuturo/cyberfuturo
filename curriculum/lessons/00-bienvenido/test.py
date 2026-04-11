"""Test for lesson 00 — bienvenido.

Checks that the student has created curriculum/hola.txt with the text
"hola mundo" followed by a newline.

Exit code: 0 on pass, 1 on fail.
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
TARGET = CURRICULUM_DIR / "hola.txt"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_exists() -> bool:
    if not TARGET.exists():
        print(f"  {FAIL} no existe el archivo {TARGET.relative_to(CURRICULUM_DIR)}")
        print(f"    {DIM}pista: usa `echo \"hola mundo\" > hola.txt` desde curriculum/{RST}")
        return False
    print(f"  {OK} {TARGET.relative_to(CURRICULUM_DIR)} existe")
    return True


def check_contents() -> bool:
    try:
        raw = TARGET.read_bytes()
    except OSError as e:
        print(f"  {FAIL} no pude leer el archivo: {e}")
        return False
    text = raw.decode("utf-8", errors="replace")
    expected = "hola mundo\n"
    if text == expected:
        print(f"  {OK} contenido correcto (\"hola mundo\\n\")")
        return True
    if text.strip() == "hola mundo":
        print(f"  {FAIL} el texto es correcto pero falta el salto de línea al final")
        print(f"    {DIM}pista: `echo \"hola mundo\" > hola.txt` agrega el \\n automáticamente{RST}")
        return False
    if "hola mundo" in text:
        print(f"  {FAIL} el archivo contiene texto extra")
        print(f"    {DIM}encontré: {text!r}{RST}")
        print(f"    {DIM}esperaba: {expected!r}{RST}")
        print(f"    {DIM}pista: puedes borrar con `rm hola.txt` y volver a intentar{RST}")
        return False
    print(f"  {FAIL} el contenido no es lo que esperaba")
    print(f"    {DIM}encontré: {text!r}{RST}")
    print(f"    {DIM}esperaba: {expected!r}{RST}")
    return False


def main() -> int:
    checks = [check_exists()]
    if checks[0]:
        checks.append(check_contents())
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
