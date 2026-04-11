"""Test for lesson 01 — navegar el sistema de archivos.

Checks that curriculum/premio.txt exists and its contents match the
hidden .premio file inside the laberinto fixture.
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
HIDDEN = CURRICULUM_DIR / "lessons" / "01-terminal" / "workspace" / "laberinto" / "piso1" / "piso2" / "piso3" / ".premio"
TARGET = CURRICULUM_DIR / "premio.txt"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_fixture() -> bool:
    if not HIDDEN.exists():
        print(f"  {FAIL} fixture missing: {HIDDEN.relative_to(CURRICULUM_DIR)}")
        print(f"    {DIM}este archivo debería venir con la lección. ¿lo borraste por accidente?{RST}")
        return False
    return True


def check_target_exists() -> bool:
    if not TARGET.exists():
        print(f"  {FAIL} no existe curriculum/premio.txt")
        print(f"    {DIM}pista: después de leer el archivo oculto, usa `cat <ruta> > premio.txt`{RST}")
        return False
    print(f"  {OK} curriculum/premio.txt existe")
    return True


def check_contents() -> bool:
    if not HIDDEN.exists():
        return False
    try:
        expected = HIDDEN.read_text(encoding="utf-8")
        actual = TARGET.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  {FAIL} no pude leer un archivo: {e}")
        return False
    if actual == expected:
        print(f"  {OK} contenido coincide con el archivo .premio escondido")
        return True
    print(f"  {FAIL} el contenido de premio.txt no coincide con el .premio original")
    print(f"    {DIM}encontré: {actual!r}{RST}")
    print(f"    {DIM}esperaba: {expected!r}{RST}")
    print(f"    {DIM}pista: busca con `find . -name .premio` desde el workspace{RST}")
    return False


def main() -> int:
    if not check_fixture():
        return 1
    if not check_target_exists():
        return 1
    if not check_contents():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
