"""CyberFuturo lesson runner.

A tiny curriculum runner, written in Python stdlib only.

Commands:
  ./cf list              Mostra todas as lições e seus status
  ./cf start [n]         Começa a lição n (ou a próxima não concluída)
  ./cf show              Reimprime as instruções da lição atual
  ./cf check             Roda o validador da lição atual
  ./cf next              Avança para a próxima lição (só depois do check passar)
  ./cf progress          Mostra o progresso geral
  ./cf help              Imprime esta ajuda
  ./cf reset             Reinicia o progresso (pede confirmação)

Internationalization:
  The runner's user-facing strings default to Portuguese (pt-BR). The language
  of the lesson MARKDOWN displayed to the student can be overridden with the
  CF_LANG environment variable:

      export CF_LANG=pt    # default: reads lesson.md
      export CF_LANG=es    # reads lesson.es.md (Spanish archive)
      export CF_LANG=en    # reads lesson.en.md (if present)

  If a language-specific lesson file doesn't exist, the runner falls back to
  lesson.md (the canonical Portuguese version).

Design notes:
  - Progress is stored in curriculum/.progress.json
  - Each lesson lives in curriculum/lessons/NN-slug/
  - A lesson folder must contain at least a lesson.md (canonical PT instructions).
  - Optional lesson.<lang>.md files provide alternative-language versions.
  - A test is curriculum/lessons/NN-slug/test.py — a script that exits 0
    on pass, non-zero on fail, and prints its feedback to stdout.
  - The runner is 100% Python stdlib. No third-party packages. Ever.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent
LESSONS_DIR = CURRICULUM_DIR / "lessons"
PROGRESS_FILE = CURRICULUM_DIR / ".progress.json"

# ---- ANSI colors (Dracula-ish) -------------------------------------------------

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
PURPLE = "\033[38;5;141m"
GREEN  = "\033[38;5;84m"
CYAN   = "\033[38;5;117m"
PINK   = "\033[38;5;212m"
YELLOW = "\033[38;5;228m"
RED    = "\033[38;5;210m"
GREY   = "\033[38;5;244m"

def color(text: str, c: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{c}{text}{RESET}"


# ---- Language detection --------------------------------------------------------

def lesson_lang() -> str:
    """Return the 2-letter language code for lesson content display.

    Reads CF_LANG env var; falls back to 'pt' (Portuguese, canonical).
    """
    lang = os.environ.get("CF_LANG", "pt").strip().lower()
    # Accept common full locale codes (e.g. pt_BR, es-419) and reduce to prefix.
    if len(lang) >= 2:
        lang = lang[:2]
    return lang or "pt"


# ---- Lesson discovery ----------------------------------------------------------

@dataclass
class Lesson:
    slug: str          # e.g. "00-bienvenido"
    number: int        # e.g. 0
    name: str          # human-readable name
    path: Path         # full path to the lesson folder
    lesson_file: Path  # the markdown to show (language-resolved)
    test_file: Path    # test.py (may not exist yet)


def resolve_lesson_file(lesson_dir: Path, lang: str) -> Path | None:
    """Pick the best lesson markdown for the requested language.

    Priority:
      1. lesson.<lang>.md  (exact language match)
      2. lesson.md         (canonical fallback, Portuguese)
    """
    exact = lesson_dir / f"lesson.{lang}.md"
    canonical = lesson_dir / "lesson.md"
    if lang != "pt" and exact.exists():
        return exact
    if canonical.exists():
        return canonical
    return None


def discover_lessons() -> list[Lesson]:
    if not LESSONS_DIR.exists():
        return []
    lang = lesson_lang()
    lessons: list[Lesson] = []
    for entry in sorted(LESSONS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        m = re.match(r"^(\d+)-(.+)$", entry.name)
        if not m:
            continue
        number = int(m.group(1))
        lesson_file = resolve_lesson_file(entry, lang)
        test_file = entry / "test.py"
        if lesson_file is None:
            continue  # skip malformed lesson dirs
        # Name is the first markdown heading of the chosen lesson file
        name = entry.name
        try:
            with lesson_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):
                        name = line.lstrip("# ").strip()
                        break
        except OSError:
            pass
        lessons.append(Lesson(
            slug=entry.name,
            number=number,
            name=name,
            path=entry,
            lesson_file=lesson_file,
            test_file=test_file,
        ))
    lessons.sort(key=lambda l: l.number)
    return lessons


# ---- Progress state ------------------------------------------------------------

def load_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {"current": None, "completed": []}
    try:
        with PROGRESS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"current": None, "completed": []}
    data.setdefault("current", None)
    data.setdefault("completed", [])
    return data


def save_progress(p: dict) -> None:
    with PROGRESS_FILE.open("w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)
        f.write("\n")


# ---- Commands ------------------------------------------------------------------

def cmd_list(lessons: list[Lesson], progress: dict) -> int:
    if not lessons:
        print(color("Nenhuma lição encontrada em curriculum/lessons/.", YELLOW))
        return 0
    print()
    print(color("  CyberFuturo — mapa de lições", PURPLE + BOLD))
    print()
    completed = set(progress.get("completed", []))
    current = progress.get("current")
    for l in lessons:
        if l.slug in completed:
            mark = color("✔", GREEN)
            status = color("feito", GREEN)
        elif l.slug == current:
            mark = color("▸", CYAN)
            status = color("atual", CYAN)
        else:
            mark = color("·", GREY)
            status = color("pendente", GREY)
        print(f"  {mark}  {color(f'{l.number:02d}', PURPLE)}  {l.name}  {DIM}[{status}{DIM}]{RESET}")
    total = len(lessons)
    done = len([l for l in lessons if l.slug in completed])
    print()
    print(f"  {DIM}progresso: {done}/{total} lições{RESET}")
    print()
    return 0


def cmd_start(lessons: list[Lesson], progress: dict, args: list[str]) -> int:
    if not lessons:
        print(color("Nenhuma lição encontrada em curriculum/lessons/.", YELLOW))
        return 1

    target: Lesson | None = None
    completed = set(progress.get("completed", []))

    if args:
        arg = args[0]
        try:
            n = int(arg)
            target = next((l for l in lessons if l.number == n), None)
        except ValueError:
            target = next((l for l in lessons if l.slug == arg or arg in l.slug), None)
        if target is None:
            print(color(f"  Nenhuma lição corresponde a '{arg}'.", RED))
            print(f"  {DIM}Tente: ./cf list{RESET}")
            return 1
    else:
        target = next((l for l in lessons if l.slug not in completed), None)
        if target is None:
            print()
            print(color("  🎉 Você concluiu todas as lições disponíveis.", GREEN + BOLD))
            print(f"  {DIM}Novas lições saem com o tempo. Rode ./cf list para conferir.{RESET}")
            print()
            return 0

    progress["current"] = target.slug
    save_progress(progress)
    _print_lesson(target)
    return 0


def cmd_show(lessons: list[Lesson], progress: dict) -> int:
    current = progress.get("current")
    if not current:
        print(color("  Nenhuma lição está ativa no momento.", YELLOW))
        print(f"  {DIM}Rode: ./cf start{RESET}")
        return 0
    lesson = next((l for l in lessons if l.slug == current), None)
    if not lesson:
        print(color(f"  A lição atual '{current}' não existe mais.", RED))
        return 1
    _print_lesson(lesson)
    return 0


def _print_lesson(lesson: Lesson) -> None:
    print()
    bar = "─" * 60
    print(color(f"  {bar}", GREY))
    print(color(f"  ▸ Lição {lesson.number:02d} — {lesson.name}", CYAN + BOLD))
    print(color(f"  {bar}", GREY))
    print()
    text = lesson.lesson_file.read_text(encoding="utf-8")
    # Strip the top-level title since we just printed it
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    for line in lines:
        if line.startswith("## "):
            print(color(f"  {line[3:]}", PURPLE + BOLD))
        elif line.startswith("### "):
            print(color(f"  {line[4:]}", CYAN))
        elif line.startswith("```"):
            print(color(f"  {line}", DIM))
        else:
            print(f"  {line}")
    print()
    print(color(f"  Quando você terminar: ./cf check", GREEN))
    print()


def cmd_check(lessons: list[Lesson], progress: dict) -> int:
    current = progress.get("current")
    if not current:
        print(color("  Nenhuma lição está ativa. Rode: ./cf start", YELLOW))
        return 1
    lesson = next((l for l in lessons if l.slug == current), None)
    if not lesson:
        print(color(f"  A lição atual '{current}' não existe mais.", RED))
        return 1
    if not lesson.test_file.exists():
        print(color(f"  A lição {lesson.number:02d} ainda não tem teste automático.", YELLOW))
        print(f"  {DIM}Marcando como concluída manualmente. Rode: ./cf next{RESET}")
        return 0

    print(color(f"  Rodando validador da lição {lesson.number:02d} — {lesson.name}...", CYAN))
    print()
    proc = subprocess.run(
        [sys.executable, str(lesson.test_file)],
        cwd=str(CURRICULUM_DIR),
        env={**os.environ, "CF_LESSON_DIR": str(lesson.path)},
    )
    print()
    if proc.returncode == 0:
        completed = progress.get("completed", [])
        if lesson.slug not in completed:
            completed.append(lesson.slug)
            progress["completed"] = completed
            save_progress(progress)
        print(color(f"  ✔ Lição {lesson.number:02d} concluída.", GREEN + BOLD))
        print(f"  {DIM}Próximo: ./cf next{RESET}")
        print()
        return 0
    else:
        print(color(f"  ✘ O validador falhou para a lição {lesson.number:02d}.", RED + BOLD))
        print(f"  {DIM}Leia o feedback acima, ajuste o que está faltando, e rode ./cf check de novo.{RESET}")
        print()
        return 1


def cmd_next(lessons: list[Lesson], progress: dict) -> int:
    current = progress.get("current")
    completed = set(progress.get("completed", []))
    if current not in completed:
        print(color("  Você ainda não concluiu a lição atual.", YELLOW))
        print(f"  {DIM}Rode: ./cf check{RESET}")
        return 1
    next_lesson = next((l for l in lessons if l.slug not in completed), None)
    if not next_lesson:
        print()
        print(color("  🎉 Você concluiu todas as lições disponíveis.", GREEN + BOLD))
        print()
        progress["current"] = None
        save_progress(progress)
        return 0
    progress["current"] = next_lesson.slug
    save_progress(progress)
    _print_lesson(next_lesson)
    return 0


def cmd_progress(lessons: list[Lesson], progress: dict) -> int:
    if not lessons:
        print(color("Nenhuma lição encontrada.", YELLOW))
        return 0
    completed = set(progress.get("completed", []))
    done = len([l for l in lessons if l.slug in completed])
    total = len(lessons)
    pct = int(100 * done / total) if total else 0
    bar_len = 28
    filled = int(bar_len * done / total) if total else 0
    bar = "█" * filled + "·" * (bar_len - filled)
    print()
    print(color(f"  progresso CyberFuturo", PURPLE + BOLD))
    print()
    print(f"  [{color(bar, GREEN)}]  {color(f'{done}/{total}', CYAN)}  {DIM}({pct}%){RESET}")
    print()
    if done == total and total > 0:
        print(color("  🎉 Todas as lições atuais concluídas. Novas chegam com o tempo.", GREEN))
    elif progress.get("current"):
        lesson = next((l for l in lessons if l.slug == progress["current"]), None)
        if lesson:
            print(f"  {DIM}atual: {color(lesson.name, CYAN)}  ({DIM}./cf show{DIM}){RESET}")
    else:
        print(f"  {DIM}nada começado ainda — rode: ./cf start{RESET}")
    print()
    return 0


def cmd_reset(progress: dict) -> int:
    try:
        reply = input("  Reiniciar todo o progresso? Isso não pode ser desfeito. [s/N] ")
    except EOFError:
        reply = ""
    if reply.strip().lower() in ("s", "y", "sim", "yes"):
        save_progress({"current": None, "completed": []})
        print(color("  Progresso reiniciado.", YELLOW))
        return 0
    print(color("  Cancelado.", GREY))
    return 0


def cmd_help() -> int:
    print(__doc__ or "")
    return 0


# ---- Main ----------------------------------------------------------------------

def main(argv: list[str]) -> int:
    lessons = discover_lessons()
    progress = load_progress()

    if not argv:
        return cmd_list(lessons, progress)

    command, *args = argv
    command = command.lower()

    if command in ("list", "ls"):
        return cmd_list(lessons, progress)
    if command == "start":
        return cmd_start(lessons, progress, args)
    if command in ("show", "current"):
        return cmd_show(lessons, progress)
    if command == "check":
        return cmd_check(lessons, progress)
    if command == "next":
        return cmd_next(lessons, progress)
    if command == "progress":
        return cmd_progress(lessons, progress)
    if command == "reset":
        return cmd_reset(progress)
    if command in ("help", "-h", "--help"):
        return cmd_help()

    print(color(f"  Comando desconhecido: {command}", RED))
    print(f"  {DIM}Tente: ./cf help{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
