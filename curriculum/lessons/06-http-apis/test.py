"""Test for lesson 06 — HTTP e APIs públicas.

Checks:
  1. curriculum/todo.json exists and is valid JSON with the expected
     fields from https://jsonplaceholder.typicode.com/todos/1
  2. curriculum/ler_todo.py exists, runs without error, and prints a
     line starting with 'Título:' followed by the value of the 'title'
     field from todo.json.

Network-offline safe: the test does NOT re-fetch the API. It validates
the student's local files against the known stable response shape of
JSONPlaceholder /todos/1.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
TODO_JSON = CURRICULUM_DIR / "todo.json"
SCRIPT = CURRICULUM_DIR / "ler_todo.py"

# The canonical response from https://jsonplaceholder.typicode.com/todos/1.
# Hardcoded here so the test works offline; JSONPlaceholder guarantees these
# fixtures are stable.
EXPECTED_ID = 1
EXPECTED_USER_ID = 1
EXPECTED_TITLE = "delectus aut autem"
EXPECTED_COMPLETED = False

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_todo_exists() -> bool:
    if not TODO_JSON.exists():
        print(f"  {FAIL} curriculum/todo.json não existe")
        print(f"    {DIM}dica: `curl -s https://jsonplaceholder.typicode.com/todos/1 > todo.json`{RST}")
        return False
    print(f"  {OK} todo.json existe")
    return True


def check_todo_valid_json() -> dict | None:
    try:
        data = json.loads(TODO_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  {FAIL} todo.json não é JSON válido: {e}")
        print(f"    {DIM}dica: refaça o curl, o arquivo pode estar vazio ou corrompido{RST}")
        return None
    except OSError as e:
        print(f"  {FAIL} não consegui ler todo.json: {e}")
        return None
    if not isinstance(data, dict):
        print(f"  {FAIL} todo.json deveria ser um objeto JSON, mas é: {type(data).__name__}")
        return None
    print(f"  {OK} todo.json é um objeto JSON válido")
    return data


def check_todo_shape(data: dict) -> bool:
    required = {"userId", "id", "title", "completed"}
    missing = required - set(data.keys())
    if missing:
        print(f"  {FAIL} todo.json está faltando campos: {', '.join(sorted(missing))}")
        print(f"    {DIM}dica: confirme que o curl foi para /todos/1 (não outro endpoint){RST}")
        return False
    print(f"  {OK} todo.json tem todos os campos esperados (userId, id, title, completed)")
    return True


def check_todo_matches_endpoint(data: dict) -> bool:
    mismatches = []
    if data.get("id") != EXPECTED_ID:
        mismatches.append(f"id deveria ser {EXPECTED_ID}, é {data.get('id')}")
    if data.get("userId") != EXPECTED_USER_ID:
        mismatches.append(f"userId deveria ser {EXPECTED_USER_ID}, é {data.get('userId')}")
    if data.get("title") != EXPECTED_TITLE:
        mismatches.append(f"title deveria ser {EXPECTED_TITLE!r}, é {data.get('title')!r}")
    if data.get("completed") != EXPECTED_COMPLETED:
        mismatches.append(f"completed deveria ser {EXPECTED_COMPLETED}, é {data.get('completed')}")
    if mismatches:
        print(f"  {FAIL} o conteúdo de todo.json não bate com /todos/1:")
        for m in mismatches:
            print(f"    {DIM}- {m}{RST}")
        print(f"    {DIM}dica: use EXATAMENTE `https://jsonplaceholder.typicode.com/todos/1`{RST}")
        return False
    print(f"  {OK} o conteúdo de todo.json corresponde ao endpoint /todos/1")
    return True


def check_script_exists() -> bool:
    if not SCRIPT.exists():
        print(f"  {FAIL} curriculum/ler_todo.py não existe")
        print(f"    {DIM}dica: crie o arquivo com o código de ~4 linhas do exemplo da lição{RST}")
        return False
    print(f"  {OK} ler_todo.py existe")
    return True


def check_script_output() -> bool:
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
    out = proc.stdout.strip()
    if not out:
        print(f"  {FAIL} o script não imprimiu nada")
        return False
    # Look for a line starting with "Título:" (optional accent tolerant)
    found = False
    for line in out.splitlines():
        lower = line.lower()
        if (lower.startswith("título:") or lower.startswith("titulo:")) and EXPECTED_TITLE in line:
            found = True
            break
    if not found:
        print(f"  {FAIL} a saída do script não contém uma linha com 'Título: {EXPECTED_TITLE}'")
        print(f"    {DIM}encontrei: {out!r}{RST}")
        print(f"    {DIM}dica: print(f\"Título: {{data['title']}}\"){RST}")
        return False
    print(f"  {OK} o script imprime 'Título: {EXPECTED_TITLE}'")
    return True


def main() -> int:
    if not check_todo_exists():
        return 1
    data = check_todo_valid_json()
    if data is None:
        return 1
    if not check_todo_shape(data):
        return 1
    if not check_todo_matches_endpoint(data):
        return 1
    if not check_script_exists():
        return 1
    if not check_script_output():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
