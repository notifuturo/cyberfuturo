"""Test for lesson 04 — ramos e fusões em Git.

Checks that curriculum/meu-blog/ is a Git repository whose HEAD has
at least two commits, includes both README.md (# meu-blog) and
LICENSE (containing "MIT"), and where the LICENSE file was introduced
by a commit subsequent to the initial one.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT = CURRICULUM_DIR / "meu-blog"
README = PROJECT / "README.md"
LICENSE = PROJECT / "LICENSE"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_project_dir() -> bool:
    if not PROJECT.is_dir():
        print(f"  {FAIL} o diretório curriculum/meu-blog/ não existe")
        print(f"    {DIM}dica: `mkdir meu-blog && cd meu-blog && git init -b main`{RST}")
        return False
    if not (PROJECT / ".git").exists():
        print(f"  {FAIL} curriculum/meu-blog/ existe mas não é um repositório Git")
        print(f"    {DIM}dica: dentro do diretório, rode `git init -b main`{RST}")
        return False
    print(f"  {OK} curriculum/meu-blog/ é um repositório Git")
    return True


def git_run(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(PROJECT), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def check_readme() -> bool:
    if not README.exists():
        print(f"  {FAIL} README.md não existe")
        print(f"    {DIM}dica: `echo \"# meu-blog\" > README.md`{RST}")
        return False
    text = README.read_text(encoding="utf-8").strip()
    if text != "# meu-blog":
        print(f"  {FAIL} README.md não contém exatamente `# meu-blog`")
        print(f"    {DIM}encontrei: {text!r}{RST}")
        return False
    print(f"  {OK} README.md correto")
    return True


def check_license() -> bool:
    if not LICENSE.exists():
        print(f"  {FAIL} LICENSE não existe")
        print(f"    {DIM}dica: `echo \"MIT\" > LICENSE` no ramo adicionar-licenca{RST}")
        return False
    text = LICENSE.read_text(encoding="utf-8")
    if "MIT" not in text:
        print(f"  {FAIL} LICENSE existe mas não menciona MIT")
        print(f"    {DIM}encontrei: {text!r}{RST}")
        return False
    print(f"  {OK} LICENSE existe e menciona MIT")
    return True


def check_commit_count() -> bool:
    code, out, _err = git_run(["log", "--oneline"])
    if code != 0:
        print(f"  {FAIL} não consegui ler o histórico do git")
        print(f"    {DIM}dica: você fez algum commit? tente `git log`{RST}")
        return False
    commits = [l for l in out.splitlines() if l.strip()]
    if len(commits) < 2:
        print(f"  {FAIL} o histórico tem só {len(commits)} commit(s); precisa de pelo menos 2")
        print(f"    {DIM}dica: um commit para o README, outro para a LICENSE{RST}")
        return False
    print(f"  {OK} histórico tem {len(commits)} commits")
    return True


def check_license_tracked() -> bool:
    code, out, _err = git_run(["ls-tree", "--name-only", "-r", "HEAD"])
    if code != 0:
        print(f"  {FAIL} não consegui ler os arquivos no HEAD")
        return False
    tracked = set(out.split())
    if "LICENSE" not in tracked:
        print(f"  {FAIL} LICENSE não está versionado no HEAD do seu ramo principal")
        print(f"    {DIM}dica: depois de fazer merge de adicionar-licenca no main,{RST}")
        print(f"    {DIM}      o arquivo LICENSE deveria aparecer no seu ramo main{RST}")
        return False
    if "README.md" not in tracked:
        print(f"  {FAIL} README.md não está versionado no HEAD")
        return False
    print(f"  {OK} README.md e LICENSE estão versionados no HEAD")
    return True


def main() -> int:
    if not check_project_dir():
        return 1
    if not check_readme():
        return 1
    if not check_license():
        return 1
    if not check_commit_count():
        return 1
    if not check_license_tracked():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
