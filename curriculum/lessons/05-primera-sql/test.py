"""Test for lesson 05 — sua primeira consulta SQL.

Checks that curriculum/biblioteca.db is a valid SQLite database containing
a `livros` table with at least 3 rows and at least 2 rows where ano >= 2000,
and that curriculum/consulta.txt contains the titles of those books.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = CURRICULUM_DIR / "biblioteca.db"
QUERY_OUTPUT = CURRICULUM_DIR / "consulta.txt"

OK   = "\033[38;5;84m✔\033[0m"
FAIL = "\033[38;5;210m✘\033[0m"
DIM  = "\033[2m"
RST  = "\033[0m"


def check_db_exists() -> bool:
    if not DB_PATH.exists():
        print(f"  {FAIL} curriculum/biblioteca.db não existe")
        print(f"    {DIM}dica: `sqlite3 biblioteca.db` cria o arquivo na primeira vez{RST}")
        return False
    # Quick magic-byte check: a SQLite file starts with "SQLite format 3\x00"
    with DB_PATH.open("rb") as f:
        magic = f.read(16)
    if magic != b"SQLite format 3\x00":
        print(f"  {FAIL} biblioteca.db existe mas não parece um banco SQLite válido")
        print(f"    {DIM}dica: apague o arquivo e crie de novo com `sqlite3 biblioteca.db`{RST}")
        return False
    print(f"  {OK} biblioteca.db existe e é um arquivo SQLite válido")
    return True


def check_livros_table() -> bool:
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='livros'")
        row = cur.fetchone()
    except sqlite3.Error as e:
        print(f"  {FAIL} erro ao consultar o banco: {e}")
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass
    if row is None:
        print(f"  {FAIL} a tabela `livros` não existe")
        print(f"    {DIM}dica: CREATE TABLE livros (id INTEGER PRIMARY KEY, titulo TEXT, autor TEXT, ano INTEGER);{RST}")
        return False
    print(f"  {OK} tabela `livros` existe")
    return True


def check_columns() -> bool:
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(livros)")
        cols = {row[1].lower(): row[2].upper() for row in cur.fetchall()}
    except sqlite3.Error as e:
        print(f"  {FAIL} erro ao consultar as colunas: {e}")
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass
    required = {"id", "titulo", "autor", "ano"}
    missing = required - set(cols.keys())
    if missing:
        print(f"  {FAIL} a tabela `livros` está faltando colunas: {', '.join(sorted(missing))}")
        print(f"    {DIM}dica: recrie a tabela com o CREATE TABLE da lição{RST}")
        return False
    print(f"  {OK} colunas encontradas: {', '.join(sorted(cols.keys()))}")
    return True


def check_rows() -> tuple[bool, list[str] | None]:
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM livros")
        total = cur.fetchone()[0]
        cur.execute("SELECT titulo FROM livros WHERE ano >= 2000 ORDER BY titulo")
        post_2000 = [r[0] for r in cur.fetchall()]
    except sqlite3.Error as e:
        print(f"  {FAIL} erro ao contar as linhas: {e}")
        return False, None
    finally:
        try:
            conn.close()
        except Exception:
            pass
    if total < 3:
        print(f"  {FAIL} só encontrei {total} livro(s); a tarefa pede pelo menos 3")
        print(f"    {DIM}dica: INSERT INTO livros (titulo, autor, ano) VALUES ('...', '...', ...);{RST}")
        return False, None
    print(f"  {OK} a tabela tem {total} livros")
    if len(post_2000) < 2:
        print(f"  {FAIL} só {len(post_2000)} livro(s) com ano >= 2000; a tarefa pede pelo menos 2")
        return False, None
    print(f"  {OK} {len(post_2000)} livros com ano >= 2000: {', '.join(post_2000)}")
    return True, post_2000


def check_query_output(expected_titles: list[str]) -> bool:
    if not QUERY_OUTPUT.exists():
        print(f"  {FAIL} curriculum/consulta.txt não existe")
        print(f"    {DIM}dica: `sqlite3 biblioteca.db \"SELECT titulo FROM livros WHERE ano >= 2000\" > consulta.txt`{RST}")
        return False
    content = QUERY_OUTPUT.read_text(encoding="utf-8")
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines:
        print(f"  {FAIL} consulta.txt existe mas está vazio")
        return False
    # Verify every expected title appears in the file (order-agnostic)
    missing = [t for t in expected_titles if t not in content]
    if missing:
        print(f"  {FAIL} consulta.txt está faltando títulos esperados: {', '.join(missing)}")
        print(f"    {DIM}encontrei: {lines}{RST}")
        return False
    print(f"  {OK} consulta.txt contém os {len(expected_titles)} títulos esperados")
    return True


def main() -> int:
    if not check_db_exists():
        return 1
    if not check_livros_table():
        return 1
    if not check_columns():
        return 1
    ok, post_2000 = check_rows()
    if not ok:
        return 1
    if not check_query_output(post_2000):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
