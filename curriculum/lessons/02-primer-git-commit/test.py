"""Test for lesson 02 — tu primer commit en Git.

Checks that curriculum/mi-proyecto/ is a valid Git repo containing a
README.md with the required content, a non-empty notas.txt, and at
least one commit that includes both files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT = CURRICULUM_DIR / "mi-proyecto"
README = PROJECT / "README.md"
NOTAS = PROJECT / "notas.txt"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_project_dir() -> bool:
    if not PROJECT.exists() or not PROJECT.is_dir():
        print(f"  {FAIL} no existe el directorio curriculum/mi-proyecto/")
        print(f"    {DIM}pista: `mkdir mi-proyecto` dentro de curriculum/{RST}")
        return False
    print(f"  {OK} existe curriculum/mi-proyecto/")
    return True


def check_readme() -> bool:
    if not README.exists():
        print(f"  {FAIL} falta README.md")
        print(f"    {DIM}pista: `echo \"# mi-proyecto\" > README.md` dentro del directorio{RST}")
        return False
    text = README.read_text(encoding="utf-8").strip()
    if text != "# mi-proyecto":
        print(f"  {FAIL} README.md no contiene exactamente `# mi-proyecto`")
        print(f"    {DIM}encontré: {text!r}{RST}")
        print(f"    {DIM}esperaba: '# mi-proyecto'{RST}")
        return False
    print(f"  {OK} README.md correcto")
    return True


def check_notas() -> bool:
    if not NOTAS.exists():
        print(f"  {FAIL} falta notas.txt")
        return False
    text = NOTAS.read_text(encoding="utf-8").strip()
    if len(text) < 3:
        print(f"  {FAIL} notas.txt existe pero está casi vacío")
        print(f"    {DIM}pista: escribe cualquier texto de al menos 3 caracteres{RST}")
        return False
    print(f"  {OK} notas.txt tiene contenido")
    return True


def check_is_git_repo() -> bool:
    git_dir = PROJECT / ".git"
    if not git_dir.exists():
        print(f"  {FAIL} curriculum/mi-proyecto/ no es un repositorio Git")
        print(f"    {DIM}pista: dentro del directorio ejecuta `git init`{RST}")
        return False
    print(f"  {OK} es un repositorio Git")
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
        print(f"  {FAIL} no hay commits en el repositorio todavía")
        print(f"    {DIM}pista: `git add .` y después `git commit -m \"mensaje\"`{RST}")
        return False
    lines = [l for l in out.splitlines() if l.strip()]
    if len(lines) < 1:
        print(f"  {FAIL} no hay commits en el repositorio todavía")
        return False
    print(f"  {OK} repositorio tiene {len(lines)} commit(s)")
    return True


def check_files_tracked() -> bool:
    code, out, _err = git_run(["ls-tree", "--name-only", "-r", "HEAD"])
    if code != 0:
        print(f"  {FAIL} no pude leer la lista de archivos de HEAD")
        return False
    tracked = set(out.split())
    missing = []
    for name in ("README.md", "notas.txt"):
        if name not in tracked:
            missing.append(name)
    if missing:
        print(f"  {FAIL} el commit no incluye: {', '.join(missing)}")
        print(f"    {DIM}pista: `git add .` y crea un commit nuevo si hace falta{RST}")
        return False
    print(f"  {OK} el commit incluye README.md y notas.txt")
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
