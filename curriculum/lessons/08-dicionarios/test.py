"""Test for lesson 08 — Dicionários e agrupamento.

Checks:
  1. curriculum/todos.json still exists, is a list of 200 items with the
     expected shape (reused from lesson 07).
  2. curriculum/por_usuario.py exists, runs without error, and prints
     exactly 10 lines matching:
        Usuário <n>: <total> tarefas, <concluidas> concluídas
     for n in 1..10, with totals and completed counts that agree with
     todos.json grouped by userId.

Network-offline safe: counts are derived from todos.json, not hardcoded.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
TODOS_JSON = CURRICULUM_DIR / "todos.json"
SCRIPT = CURRICULUM_DIR / "por_usuario.py"

EXPECTED_TOTAL = 200
EXPECTED_USERS = list(range(1, 11))  # JSONPlaceholder has userId 1..10
REQUIRED_FIELDS = {"userId", "id", "title", "completed"}

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_todos() -> list | None:
    if not TODOS_JSON.exists():
        print(f"  {FAIL} curriculum/todos.json não existe")
        print(f"    {DIM}dica: baixa de novo com o curl da lição 07{RST}")
        return None
    try:
        data = json.loads(TODOS_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  {FAIL} não consegui ler todos.json: {e}")
        return None
    if not isinstance(data, list) or len(data) != EXPECTED_TOTAL:
        print(f"  {FAIL} todos.json deveria ser uma lista de {EXPECTED_TOTAL} itens")
        return None
    first = data[0] if data else {}
    if not isinstance(first, dict) or REQUIRED_FIELDS - set(first.keys()):
        print(f"  {FAIL} os itens de todos.json estão com o formato errado")
        return None
    print(f"  {OK} todos.json ok ({EXPECTED_TOTAL} itens)")
    return data


def expected_groups(data: list) -> dict[int, tuple[int, int]]:
    groups: dict[int, list[int]] = {}
    for t in data:
        uid = t.get("userId")
        if not isinstance(uid, int):
            continue
        slot = groups.setdefault(uid, [0, 0])
        slot[0] += 1
        if t.get("completed") is True:
            slot[1] += 1
    return {u: (t, c) for u, (t, c) in groups.items()}


def check_script_exists() -> bool:
    if not SCRIPT.exists():
        print(f"  {FAIL} curriculum/por_usuario.py não existe")
        print(f"    {DIM}dica: a lição tem um exemplo de ~10 linhas com setdefault{RST}")
        return False
    print(f"  {OK} por_usuario.py existe")
    return True


LINE_RE = re.compile(
    r"^\s*usu[áa]rio\s+(\d+)\s*:\s*(\d+)\s+tarefas?\s*,\s*(\d+)\s+conclu[ií]das?\s*$",
    re.IGNORECASE,
)


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

    out_lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if len(out_lines) < len(EXPECTED_USERS):
        print(f"  {FAIL} o script deveria imprimir ao menos {len(EXPECTED_USERS)} linhas, imprimiu {len(out_lines)}")
        print(f"    {DIM}saída: {proc.stdout!r}{RST}")
        return False

    groups = expected_groups(data)

    parsed: dict[int, tuple[int, int]] = {}
    seen_order: list[int] = []
    for line in out_lines:
        m = LINE_RE.match(line)
        if not m:
            continue
        uid = int(m.group(1))
        total = int(m.group(2))
        done = int(m.group(3))
        parsed[uid] = (total, done)
        seen_order.append(uid)

    if len(parsed) < len(EXPECTED_USERS):
        print(f"  {FAIL} não encontrei uma linha válida pra cada usuário (1..10)")
        print(f"    {DIM}formato esperado: 'Usuário N: X tarefas, Y concluídas'{RST}")
        return False

    for u in EXPECTED_USERS:
        if u not in parsed:
            print(f"  {FAIL} faltou a linha do usuário {u}")
            return False
        exp_total, exp_done = groups.get(u, (0, 0))
        got_total, got_done = parsed[u]
        if got_total != exp_total:
            print(f"  {FAIL} usuário {u}: total impresso = {got_total}, esperado = {exp_total}")
            return False
        if got_done != exp_done:
            print(f"  {FAIL} usuário {u}: concluídas impressas = {got_done}, esperado = {exp_done}")
            print(f"    {DIM}dica: conte só os itens desse usuário com completed == true{RST}")
            return False

    # Ordering: first ten recognized lines should be users 1..10 in order.
    recognized = [u for u in seen_order if u in set(EXPECTED_USERS)]
    if recognized[: len(EXPECTED_USERS)] != EXPECTED_USERS:
        print(f"  {FAIL} as linhas deveriam sair em ordem do usuário 1 ao 10")
        print(f"    {DIM}saíram: {recognized[:len(EXPECTED_USERS)]}{RST}")
        print(f"    {DIM}dica: `for u in sorted(contagem)`{RST}")
        return False

    print(f"  {OK} o script agrupa por usuário corretamente (1..10)")
    return True


def main() -> int:
    data = check_todos()
    if data is None:
        return 1
    if not check_script_exists():
        return 1
    if not check_script_output(data):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
