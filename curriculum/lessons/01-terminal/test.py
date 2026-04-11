"""Test for lesson 01 — navegar o sistema de arquivos.

Checks that curriculum/premio.txt exists and its contents match the
hidden .premio file inside the labirinto fixture.
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
HIDDEN = CURRICULUM_DIR / "lessons" / "01-terminal" / "workspace" / "labirinto" / "piso1" / "piso2" / "piso3" / ".premio"
TARGET = CURRICULUM_DIR / "premio.txt"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_fixture() -> bool:
    if not HIDDEN.exists():
        print(f"  {FAIL} fixture faltando: {HIDDEN.relative_to(CURRICULUM_DIR)}")
        print(f"    {DIM}esse arquivo deveria vir com a lição. você apagou sem querer?{RST}")
        return False
    return True


def check_target_exists() -> bool:
    if not TARGET.exists():
        print(f"  {FAIL} curriculum/premio.txt não existe")
        print(f"    {DIM}dica: depois de ler o arquivo oculto, use `cat <caminho> > premio.txt`{RST}")
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
        print(f"  {FAIL} não consegui ler um dos arquivos: {e}")
        return False
    if actual == expected:
        print(f"  {OK} conteúdo bate com o arquivo .premio escondido")
        return True
    print(f"  {FAIL} o conteúdo de premio.txt não bate com o .premio original")
    print(f"    {DIM}encontrei: {actual!r}{RST}")
    print(f"    {DIM}esperava:  {expected!r}{RST}")
    print(f"    {DIM}dica: busque com `find . -name .premio` a partir do workspace{RST}")
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
