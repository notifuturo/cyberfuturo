"""CyberFuturo lesson runner.

A tiny curriculum runner, written in Python stdlib only.

Commands:
  ./cf list              Show all lessons and their status
  ./cf start [n]         Start lesson n (or the next incomplete one)
  ./cf show              Re-print the current lesson instructions
  ./cf check             Run the test for the current lesson
  ./cf next              Advance to the next lesson (only after check passes)
  ./cf progress          Show progress summary
  ./cf help              Print this help
  ./cf reset             Reset progress (asks for confirmation)

Design notes:
  - Progress is stored in curriculum/.progress.json
  - Each lesson lives in curriculum/lessons/NN-slug/
  - A lesson folder must contain at least a lesson.md (instructions).
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


# ---- Lesson discovery ----------------------------------------------------------

@dataclass
class Lesson:
    slug: str          # e.g. "00-bienvenido"
    number: int        # e.g. 0
    name: str          # human-readable name
    path: Path         # full path to the lesson folder
    lesson_file: Path  # lesson.md
    test_file: Path    # test.py (may not exist yet)


def discover_lessons() -> list[Lesson]:
    if not LESSONS_DIR.exists():
        return []
    lessons: list[Lesson] = []
    for entry in sorted(LESSONS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        m = re.match(r"^(\d+)-(.+)$", entry.name)
        if not m:
            continue
        number = int(m.group(1))
        lesson_file = entry / "lesson.md"
        test_file = entry / "test.py"
        if not lesson_file.exists():
            continue  # skip malformed lesson dirs
        # Name is the first markdown heading of lesson.md, if present
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
        print(color("No lessons found under curriculum/lessons/.", YELLOW))
        return 0
    print()
    print(color("  CyberFuturo — lesson map", PURPLE + BOLD))
    print()
    completed = set(progress.get("completed", []))
    current = progress.get("current")
    for l in lessons:
        if l.slug in completed:
            mark = color("✔", GREEN)
            status = color("done", GREEN)
        elif l.slug == current:
            mark = color("▸", CYAN)
            status = color("current", CYAN)
        else:
            mark = color("·", GREY)
            status = color("pending", GREY)
        print(f"  {mark}  {color(f'{l.number:02d}', PURPLE)}  {l.name}  {DIM}[{status}{DIM}]{RESET}")
    total = len(lessons)
    done = len([l for l in lessons if l.slug in completed])
    print()
    print(f"  {DIM}progress: {done}/{total} lessons{RESET}")
    print()
    return 0


def cmd_start(lessons: list[Lesson], progress: dict, args: list[str]) -> int:
    if not lessons:
        print(color("No lessons found under curriculum/lessons/.", YELLOW))
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
            print(color(f"  No lesson matches '{arg}'.", RED))
            print(f"  {DIM}Try: ./cf list{RESET}")
            return 1
    else:
        target = next((l for l in lessons if l.slug not in completed), None)
        if target is None:
            print()
            print(color("  🎉 You've completed every available lesson.", GREEN + BOLD))
            print(f"  {DIM}New lessons are added over time. Run ./cf list to check.{RESET}")
            print()
            return 0

    progress["current"] = target.slug
    save_progress(progress)
    _print_lesson(target)
    return 0


def cmd_show(lessons: list[Lesson], progress: dict) -> int:
    current = progress.get("current")
    if not current:
        print(color("  No lesson is currently active.", YELLOW))
        print(f"  {DIM}Run: ./cf start{RESET}")
        return 0
    lesson = next((l for l in lessons if l.slug == current), None)
    if not lesson:
        print(color(f"  Current lesson '{current}' no longer exists.", RED))
        return 1
    _print_lesson(lesson)
    return 0


def _print_lesson(lesson: Lesson) -> None:
    print()
    bar = "─" * 60
    print(color(f"  {bar}", GREY))
    print(color(f"  ▸ Lesson {lesson.number:02d} — {lesson.name}", CYAN + BOLD))
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
    print(color(f"  When you're done: ./cf check", GREEN))
    print()


def cmd_check(lessons: list[Lesson], progress: dict) -> int:
    current = progress.get("current")
    if not current:
        print(color("  No lesson is currently active. Run: ./cf start", YELLOW))
        return 1
    lesson = next((l for l in lessons if l.slug == current), None)
    if not lesson:
        print(color(f"  Current lesson '{current}' no longer exists.", RED))
        return 1
    if not lesson.test_file.exists():
        print(color(f"  Lesson {lesson.number:02d} has no automated test yet.", YELLOW))
        print(f"  {DIM}Marking as complete manually. Run: ./cf next{RESET}")
        return 0

    print(color(f"  Running checks for lesson {lesson.number:02d} — {lesson.name}...", CYAN))
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
        print(color(f"  ✔ Lesson {lesson.number:02d} complete.", GREEN + BOLD))
        print(f"  {DIM}Next: ./cf next{RESET}")
        print()
        return 0
    else:
        print(color(f"  ✘ Checks failed for lesson {lesson.number:02d}.", RED + BOLD))
        print(f"  {DIM}Read the feedback above, fix what's missing, then run ./cf check again.{RESET}")
        print()
        return 1


def cmd_next(lessons: list[Lesson], progress: dict) -> int:
    current = progress.get("current")
    completed = set(progress.get("completed", []))
    if current not in completed:
        print(color("  You haven't completed the current lesson yet.", YELLOW))
        print(f"  {DIM}Run: ./cf check{RESET}")
        return 1
    next_lesson = next((l for l in lessons if l.slug not in completed), None)
    if not next_lesson:
        print()
        print(color("  🎉 You've completed every available lesson.", GREEN + BOLD))
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
        print(color("No lessons found.", YELLOW))
        return 0
    completed = set(progress.get("completed", []))
    done = len([l for l in lessons if l.slug in completed])
    total = len(lessons)
    pct = int(100 * done / total) if total else 0
    bar_len = 28
    filled = int(bar_len * done / total) if total else 0
    bar = "█" * filled + "·" * (bar_len - filled)
    print()
    print(color(f"  CyberFuturo progress", PURPLE + BOLD))
    print()
    print(f"  [{color(bar, GREEN)}]  {color(f'{done}/{total}', CYAN)}  {DIM}({pct}%){RESET}")
    print()
    if done == total and total > 0:
        print(color("  🎉 All current lessons complete. New ones land over time.", GREEN))
    elif progress.get("current"):
        lesson = next((l for l in lessons if l.slug == progress["current"]), None)
        if lesson:
            print(f"  {DIM}current: {color(lesson.name, CYAN)}  ({DIM}./cf show{DIM}){RESET}")
    else:
        print(f"  {DIM}nothing started yet — run: ./cf start{RESET}")
    print()
    return 0


def cmd_reset(progress: dict) -> int:
    try:
        reply = input("  Reset all progress? This cannot be undone. [y/N] ")
    except EOFError:
        reply = ""
    if reply.strip().lower() in ("y", "yes"):
        save_progress({"current": None, "completed": []})
        print(color("  Progress reset.", YELLOW))
        return 0
    print(color("  Cancelled.", GREY))
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

    print(color(f"  Unknown command: {command}", RED))
    print(f"  {DIM}Try: ./cf help{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
