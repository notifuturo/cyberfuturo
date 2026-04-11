"""Test for lesson 00 — boas-vindas.

Checks that the student has created curriculum/ola.txt with the text
"olá mundo" followed by a newline.

Exit code: 0 on pass, 1 on fail.
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
TARGET = CURRICULUM_DIR / "ola.txt"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_exists() -> bool:
    if not TARGET.exists():
        print(f"  {FAIL} o arquivo {TARGET.relative_to(CURRICULUM_DIR)} não existe")
        print(f"    {DIM}dica: use `echo \"olá mundo\" > ola.txt` dentro de curriculum/{RST}")
        return False
    print(f"  {OK} {TARGET.relative_to(CURRICULUM_DIR)} existe")
    return True


def check_contents() -> bool:
    try:
        raw = TARGET.read_bytes()
    except OSError as e:
        print(f"  {FAIL} não consegui ler o arquivo: {e}")
        return False
    text = raw.decode("utf-8", errors="replace")
    expected = "olá mundo\n"
    if text == expected:
        print(f"  {OK} conteúdo correto (\"olá mundo\\n\")")
        return True
    if text.strip() == "olá mundo":
        print(f"  {FAIL} o texto está correto, mas falta a quebra de linha no final")
        print(f"    {DIM}dica: `echo \"olá mundo\" > ola.txt` já adiciona o \\n automaticamente{RST}")
        return False
    if "olá mundo" in text or "ola mundo" in text:
        print(f"  {FAIL} o arquivo contém texto extra")
        print(f"    {DIM}encontrei: {text!r}{RST}")
        print(f"    {DIM}esperava:  {expected!r}{RST}")
        print(f"    {DIM}dica: você pode apagar com `rm ola.txt` e tentar de novo{RST}")
        return False
    print(f"  {FAIL} o conteúdo não é o que eu esperava")
    print(f"    {DIM}encontrei: {text!r}{RST}")
    print(f"    {DIM}esperava:  {expected!r}{RST}")
    return False


def main() -> int:
    checks = [check_exists()]
    if checks[0]:
        checks.append(check_contents())
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
