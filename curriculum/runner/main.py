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
  ./cf telemetry status  Mostra o estado da telemetria anônima
  ./cf telemetry on      Ativa a telemetria
  ./cf telemetry off     Desativa a telemetria
  ./cf telemetry forget  Apaga o anon_id local e pede ao servidor pra apagar os registros
  ./cf activate CODIGO   Vincula sua compra ao workspace (desbloqueia certificados)

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
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path

CURRICULUM_DIR = Path(__file__).resolve().parent.parent
LESSONS_DIR = CURRICULUM_DIR / "lessons"
PROGRESS_FILE = CURRICULUM_DIR / ".progress.json"

TELEMETRY_ENDPOINT = "https://cyberfuturo.com/api/ping"
TELEMETRY_TIMEOUT_S = 2.0   # ping must not slow the runner perceptibly
ACTIVATE_ENDPOINT  = "https://cyberfuturo.com/api/activate"
ACTIVATE_TIMEOUT_S = 5.0    # activation is user-initiated; ok to wait a little

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
    data.setdefault("telemetry_opt_in", None)   # None = never asked, True/False = decided
    data.setdefault("anon_id", None)             # set only if opted in
    data.setdefault("pinged", {"start": [], "pass": []})
    return data


def save_progress(p: dict) -> None:
    with PROGRESS_FILE.open("w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)
        f.write("\n")


# ---- Telemetry -----------------------------------------------------------------

TELEMETRY_PROMPT = {
    "pt": (
        "\n"
        "  O CyberFuturo quer contar quantas pessoas começam e concluem cada lição.\n"
        "  Se você topar, a gente manda um ping anônimo (só o nome da lição, o idioma\n"
        "  e um ID aleatório gerado agora no seu workspace) pro site.\n"
        "\n"
        "  Não coletamos email, código, IP, ou qualquer coisa que te identifique.\n"
        "  Detalhes em https://cyberfuturo.com/pt/privacidade/\n"
        "\n"
        "  Topar? [s/N]: "
    ),
    "es": (
        "\n"
        "  CyberFuturo quiere contar cuántas personas empiezan y terminan cada lección.\n"
        "  Si aceptas, enviamos un ping anónimo (solo el slug de la lección, el idioma\n"
        "  y un ID aleatorio generado ahora en tu workspace) al sitio.\n"
        "\n"
        "  No recogemos email, código, IP, ni nada que te identifique.\n"
        "  Detalles en https://cyberfuturo.com/es/privacidad/\n"
        "\n"
        "  ¿Aceptas? [s/N]: "
    ),
    "en": (
        "\n"
        "  CyberFuturo would like to count how many people start and finish each lesson.\n"
        "  If you opt in, we send an anonymous ping (just the lesson slug, the language,\n"
        "  and a random ID generated right now in your workspace) to the site.\n"
        "\n"
        "  We do not collect email, code, IP, or anything that could identify you.\n"
        "  Details at https://cyberfuturo.com/en/privacy/\n"
        "\n"
        "  Opt in? [y/N]: "
    ),
    "fr": (
        "\n"
        "  CyberFuturo aimerait compter combien de personnes commencent et terminent chaque leçon.\n"
        "  Si vous acceptez, nous envoyons un ping anonyme (juste le slug de la leçon, la langue\n"
        "  et un ID aléatoire généré maintenant dans votre workspace) au site.\n"
        "\n"
        "  Nous ne collectons ni e-mail, ni code, ni IP, ni rien qui puisse vous identifier.\n"
        "  Détails sur https://cyberfuturo.com/fr/confidentialite/\n"
        "\n"
        "  Accepter? [o/N]: "
    ),
}

_YES_ANSWERS = {"s", "sim", "y", "yes", "o", "oui", "si", "sí"}


def maybe_prompt_telemetry(progress: dict) -> None:
    """Ask the student once, on the first command that counts, whether to opt in.

    Silent no-op if:
      - the user has already answered (True or False)
      - stdin/stdout are not a TTY (Codespaces web UI falls through to the editor;
        we don't want to block non-interactive flows or CI)
      - the CF_TELEMETRY_DISABLED env var is set (escape hatch for operators)
    """
    if progress.get("telemetry_opt_in") is not None:
        return
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return
    if os.environ.get("CF_TELEMETRY_DISABLED"):
        progress["telemetry_opt_in"] = False
        save_progress(progress)
        return

    lang = lesson_lang()
    prompt = TELEMETRY_PROMPT.get(lang, TELEMETRY_PROMPT["pt"])
    try:
        answer = input(prompt).strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        progress["telemetry_opt_in"] = False
        save_progress(progress)
        return

    if answer in _YES_ANSWERS:
        progress["telemetry_opt_in"] = True
        progress["anon_id"] = str(uuid.uuid4())
    else:
        progress["telemetry_opt_in"] = False
    save_progress(progress)


def ping(progress: dict, event: str, lesson_slug: str) -> None:
    """Send a telemetry event. Silent failure on network errors — never blocks the user.

    Guarantees:
      - No-op if the user declined, or never opted in
      - No-op if this (event, lesson_slug) has already been pinged from this workspace
      - Never raises
      - Never takes more than TELEMETRY_TIMEOUT_S to return
    """
    if not progress.get("telemetry_opt_in"):
        return
    anon_id = progress.get("anon_id")
    if not anon_id:
        return
    pinged = progress.setdefault("pinged", {"start": [], "pass": []})
    slot = pinged.setdefault(event, [])
    if lesson_slug in slot:
        return

    payload = json.dumps({
        "event":   event,
        "lesson":  lesson_slug,
        "lang":    lesson_lang(),
        "anon_id": anon_id,
    }).encode("utf-8")
    req = urllib.request.Request(
        TELEMETRY_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TELEMETRY_TIMEOUT_S) as resp:
            if 200 <= resp.status < 300:
                slot.append(lesson_slug)
                save_progress(progress)
    except (urllib.error.URLError, TimeoutError, OSError):
        # Fire-and-forget. If the endpoint is down, we silently drop the event.
        # The local .progress.json is untouched so we'll try again next time.
        pass


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
    maybe_prompt_telemetry(progress)
    ping(progress, "start", target.slug)
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

    # Validate that the test file resides inside the lessons directory to
    # prevent path-traversal attacks (e.g. via symlinks).
    resolved_test = lesson.test_file.resolve()
    resolved_lessons = LESSONS_DIR.resolve()
    if not str(resolved_test).startswith(str(resolved_lessons) + os.sep):
        print(color(f"  ✘ Caminho do teste está fora do diretório de lições: {resolved_test}", RED))
        return 1

    print(color(f"  Rodando validador da lição {lesson.number:02d} — {lesson.name}...", CYAN))
    print()
    proc = subprocess.run(
        [sys.executable, str(resolved_test)],
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
        ping(progress, "pass", lesson.slug)
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


def cmd_telemetry(progress: dict, args: list[str]) -> int:
    sub = (args[0] if args else "status").lower()
    if sub == "status":
        state = progress.get("telemetry_opt_in")
        if state is True:
            print(color(f"  Telemetria: ATIVADA. anon_id={progress.get('anon_id')}", GREEN))
        elif state is False:
            print(color("  Telemetria: DESATIVADA.", GREY))
        else:
            print(color("  Telemetria: ainda não perguntada.", YELLOW))
        return 0
    if sub == "on":
        progress["telemetry_opt_in"] = True
        if not progress.get("anon_id"):
            progress["anon_id"] = str(uuid.uuid4())
        save_progress(progress)
        print(color("  Telemetria ativada.", GREEN))
        return 0
    if sub == "off":
        progress["telemetry_opt_in"] = False
        save_progress(progress)
        print(color("  Telemetria desativada.", YELLOW))
        return 0
    if sub == "forget":
        anon_id = progress.get("anon_id")
        if anon_id:
            payload = json.dumps({"anon_id": anon_id}).encode("utf-8")
            req = urllib.request.Request(
                TELEMETRY_ENDPOINT, data=payload,
                headers={"Content-Type": "application/json"},
                method="DELETE",
            )
            try:
                urllib.request.urlopen(req, timeout=TELEMETRY_TIMEOUT_S).read()
            except Exception:
                pass
        progress["telemetry_opt_in"] = False
        progress["anon_id"] = None
        progress["pinged"] = {"start": [], "pass": []}
        save_progress(progress)
        print(color("  anon_id local removido. Servidor avisado.", YELLOW))
        return 0
    print(color(f"  Uso: ./cf telemetry [status|on|off|forget]", RED))
    return 1


def cmd_activate(progress: dict, args: list[str]) -> int:
    if not args:
        print(color("  Uso: ./cf activate CODIGO", RED))
        return 1
    code = args[0].strip().upper()

    # Activation needs an anon_id. If the student skipped the telemetry prompt,
    # generate one now — activation implies consent to completion pings
    # (buyers need those pings to earn handouts and certificates).
    anon_id = progress.get("anon_id")
    if not anon_id:
        anon_id = str(uuid.uuid4())
        progress["anon_id"] = anon_id
        progress["telemetry_opt_in"] = True
        save_progress(progress)

    payload = json.dumps({"code": code, "anon_id": anon_id}).encode("utf-8")
    req = urllib.request.Request(
        ACTIVATE_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=ACTIVATE_TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8")).get("error", f"HTTP {e.code}")
        except Exception:
            err = f"HTTP {e.code}"
        print(color(f"  ✘ {err}", RED))
        return 1
    except (urllib.error.URLError, TimeoutError, OSError):
        print(color("  ✘ Não consegui falar com o servidor. Tente de novo.", RED))
        return 1

    if not data.get("ok"):
        print(color(f"  ✘ {data.get('error', 'activation failed')}", RED))
        return 1

    progress["activated"] = True
    progress["verify_url"] = data.get("verify_url")
    save_progress(progress)

    print(color("  ✔ Conta vinculada.", GREEN + BOLD))
    print(f"  {DIM}Sua página pessoal: {data.get('verify_url')}{RESET}")
    print(f"  {DIM}Cada capítulo concluído gera um handout lá.{RESET}")
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
    if command == "telemetry":
        return cmd_telemetry(progress, args)
    if command == "activate":
        return cmd_activate(progress, args)
    if command in ("help", "-h", "--help"):
        return cmd_help()

    print(color(f"  Comando desconhecido: {command}", RED))
    print(f"  {DIM}Tente: ./cf help{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
