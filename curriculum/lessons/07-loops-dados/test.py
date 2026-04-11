"""Test for lesson 07 — Loops com dados reais.

Checks:
  1. curriculum/todos.json exists, is valid JSON, is a list of 200 items,
     and each item has the expected shape from
     https://jsonplaceholder.typicode.com/todos.
  2. curriculum/contar_todos.py exists, runs without error, and prints
     exactly three lines matching:
        Total: 200
        Concluídas: <n>
        Pendentes: <n>
     where concluídas + pendentes == 200 and both counts agree with
     todos.json.

Network-offline safe: the test does NOT re-fetch the API. JSONPlaceholder
guarantees the /todos fixture is stable (200 items, 90 completed, 110 pending
as of this writing, but we compute from the file rather than hardcoding so
a future JSONPlaceholder tweak doesn't silently break the lesson).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
TODOS_JSON = CURRICULUM_DIR / "todos.json"
SCRIPT = CURRICULUM_DIR / "contar_todos.py"

EXPECTED_TOTAL = 200
REQUIRED_FIELDS = {"userId", "id", "title", "completed"}

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_todos_exists() -> bool:
    if not TODOS_JSON.exists():
        print(f"  {FAIL} curriculum/todos.json não existe")
        print(f"    {DIM}dica: `curl -s https://jsonplaceholder.typicode.com/todos > todos.json`{RST}")
        return False
    print(f"  {OK} todos.json existe")
    return True


def check_todos_valid_json() -> list | None:
    try:
        data = json.loads(TODOS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  {FAIL} todos.json não é JSON válido: {e}")
        return None
    except OSError as e:
        print(f"  {FAIL} não consegui ler todos.json: {e}")
        return None
    if not isinstance(data, list):
        print(f"  {FAIL} todos.json deveria ser uma LISTA JSON, mas é: {type(data).__name__}")
        print(f"    {DIM}dica: você pegou /todos/1? tira o /1, a gente quer a lista inteira{RST}")
        return None
    print(f"  {OK} todos.json é uma lista JSON válida")
    return data


def check_todos_shape(data: list) -> bool:
    if len(data) != EXPECTED_TOTAL:
        print(f"  {FAIL} todos.json deveria ter {EXPECTED_TOTAL} itens, tem {len(data)}")
        print(f"    {DIM}dica: confirme que o curl foi pro endpoint certo, sem filtros{RST}")
        return False
    print(f"  {OK} todos.json tem {EXPECTED_TOTAL} itens")
    # Spot-check the first item has the right fields.
    first = data[0]
    if not isinstance(first, dict):
        print(f"  {FAIL} os itens da lista deveriam ser objetos, mas o primeiro é: {type(first).__name__}")
        return False
    missing = REQUIRED_FIELDS - set(first.keys())
    if missing:
        print(f"  {FAIL} os itens estão faltando campos: {', '.join(sorted(missing))}")
        return False
    print(f"  {OK} os itens têm os campos esperados (userId, id, title, completed)")
    return True


def expected_counts(data: list) -> tuple[int, int]:
    completed = sum(1 for t in data if t.get("completed") is True)
    pending = sum(1 for t in data if t.get("completed") is False)
    return completed, pending


def check_script_exists() -> bool:
    if not SCRIPT.exists():
        print(f"  {FAIL} curriculum/contar_todos.py não existe")
        print(f"    {DIM}dica: tem um exemplo de ~8 linhas na lição, lê antes de copiar{RST}")
        return False
    print(f"  {OK} contar_todos.py existe")
    return True


def check_script_output(data: list) -> bool:
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(CURRICULUM_DIR),
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        print(f"  {FAIL} o script demorou demais (timeout)")
        return False
    if proc.returncode != 0:
        print(f"  {FAIL} o script terminou com erro (exit={proc.returncode})")
        if proc.stderr.strip():
            for line in proc.stderr.strip().splitlines()[:5]:
                print(f"    {DIM}{line}{RST}")
        return False

    out_lines = [ln.rstrip() for ln in proc.stdout.strip().splitlines() if ln.strip()]
    if len(out_lines) < 3:
        print(f"  {FAIL} o script deveria imprimir 3 linhas, imprimiu {len(out_lines)}")
        print(f"    {DIM}saída: {proc.stdout!r}{RST}")
        return False

    patterns = [
        re.compile(r"^\s*total\s*:\s*(\d+)\s*$", re.IGNORECASE),
        re.compile(r"^\s*conclu[ií]das?\s*:\s*(\d+)\s*$", re.IGNORECASE),
        re.compile(r"^\s*pendentes?\s*:\s*(\d+)\s*$", re.IGNORECASE),
    ]
    labels = ["Total", "Concluídas", "Pendentes"]
    matches: list[int] = []
    for i, (line, pat, label) in enumerate(zip(out_lines[:3], patterns, labels)):
        m = pat.match(line)
        if not m:
            print(f"  {FAIL} linha {i+1} deveria ser '{label}: <número>', é: {line!r}")
            return False
        matches.append(int(m.group(1)))

    total_printed, completed_printed, pending_printed = matches
    exp_completed, exp_pending = expected_counts(data)

    if total_printed != EXPECTED_TOTAL:
        print(f"  {FAIL} total impresso é {total_printed}, deveria ser {EXPECTED_TOTAL}")
        return False
    if completed_printed != exp_completed:
        print(f"  {FAIL} concluídas impressas = {completed_printed}, deveria ser {exp_completed}")
        print(f"    {DIM}dica: conte só os itens com completed == true{RST}")
        return False
    if pending_printed != exp_pending:
        print(f"  {FAIL} pendentes impressas = {pending_printed}, deveria ser {exp_pending}")
        print(f"    {DIM}dica: pendentes = total - concluídas (ou conte completed == false){RST}")
        return False
    if completed_printed + pending_printed != total_printed:
        print(f"  {FAIL} concluídas ({completed_printed}) + pendentes ({pending_printed}) != total ({total_printed})")
        return False

    print(f"  {OK} o script imprime Total/Concluídas/Pendentes com os números certos")
    return True


def main() -> int:
    if not check_todos_exists():
        return 1
    data = check_todos_valid_json()
    if data is None:
        return 1
    if not check_todos_shape(data):
        return 1
    if not check_script_exists():
        return 1
    if not check_script_output(data):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
