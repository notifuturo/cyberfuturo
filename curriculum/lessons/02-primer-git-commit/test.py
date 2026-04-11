"""Test for lesson 02 — seu primeiro commit em Git.

Checks that curriculum/meu-projeto/ is a valid Git repo containing a
README.md with the required content, a non-empty notas.txt, and at
least one commit that includes both files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT = CURRICULUM_DIR / "meu-projeto"
README = PROJECT / "README.md"
NOTAS = PROJECT / "notas.txt"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_project_dir() -> bool:
    if not PROJECT.exists() or not PROJECT.is_dir():
        print(f"  {FAIL} o diretório curriculum/meu-projeto/ não existe")
        print(f"    {DIM}dica: `mkdir meu-projeto` dentro de curriculum/{RST}")
        return False
    print(f"  {OK} curriculum/meu-projeto/ existe")
    return True


def check_readme() -> bool:
    if not README.exists():
        print(f"  {FAIL} README.md faltando")
        print(f"    {DIM}dica: `echo \"# meu-projeto\" > README.md` dentro do diretório{RST}")
        return False
    text = README.read_text(encoding="utf-8").strip()
    if text != "# meu-projeto":
        print(f"  {FAIL} README.md não contém exatamente `# meu-projeto`")
        print(f"    {DIM}encontrei: {text!r}{RST}")
        print(f"    {DIM}esperava:  '# meu-projeto'{RST}")
        return False
    print(f"  {OK} README.md correto")
    return True


def check_notas() -> bool:
    if not NOTAS.exists():
        print(f"  {FAIL} notas.txt faltando")
        return False
    text = NOTAS.read_text(encoding="utf-8").strip()
    if len(text) < 3:
        print(f"  {FAIL} notas.txt existe mas está quase vazio")
        print(f"    {DIM}dica: escreva qualquer texto com pelo menos 3 caracteres{RST}")
        return False
    print(f"  {OK} notas.txt tem conteúdo")
    return True


def check_is_git_repo() -> bool:
    git_dir = PROJECT / ".git"
    if not git_dir.exists():
        print(f"  {FAIL} curriculum/meu-projeto/ não é um repositório Git")
        print(f"    {DIM}dica: dentro do diretório, rode `git init`{RST}")
        return False
    print(f"  {OK} é um repositório Git")
    return True


def git_run(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(PROJECT), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def check_has_commit() -> bool:
    code, out, _err = git_run(["log", "--oneline"])
    if code != 0:
        print(f"  {FAIL} ainda não tem commits no repositório")
        print(f"    {DIM}dica: `git add .` e depois `git commit -m \"mensagem\"`{RST}")
        return False
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) < 1:
        print(f"  {FAIL} ainda não tem commits no repositório")
        return False
    print(f"  {OK} o repositório tem {len(lines)} commit(s)")
    return True


def check_files_tracked() -> bool:
    code, out, _err = git_run(["ls-tree", "--name-only", "-r", "HEAD"])
    if code != 0:
        print(f"  {FAIL} não consegui ler a lista de arquivos do HEAD")
        return False
    tracked = set(out.split())
    missing = []
    for name in ("README.md", "notas.txt"):
        if name not in tracked:
            missing.append(name)
    if missing:
        print(f"  {FAIL} o commit não inclui: {', '.join(missing)}")
        print(f"    {DIM}dica: `git add .` e crie um commit novo se precisar{RST}")
        return False
    print(f"  {OK} o commit inclui README.md e notas.txt")
    return True


def main() -> int:
    checks = [
        check_project_dir(),
        check_readme(),
        check_notas(),
        check_is_git_repo(),
    ]
    if not all(checks):
        return 1
    if not check_has_commit():
        return 1
    if not check_files_tracked():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
