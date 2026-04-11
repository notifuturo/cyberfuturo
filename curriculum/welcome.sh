#!/usr/bin/env bash
# CyberFuturo — welcome script shown when the Codespace first attaches.
# No dependencies. Pure bash.

cd "$(dirname "$0")" || exit 0

# ANSI colors that match the brand (Dracula-ish)
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_DIM="\033[2m"
C_PURPLE="\033[38;5;141m"
C_GREEN="\033[38;5;84m"
C_CYAN="\033[38;5;117m"
C_PINK="\033[38;5;212m"
C_YELLOW="\033[38;5;228m"

cat <<'BANNER'

   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███████╗██╗   ██╗████████╗██╗   ██╗██████╗  ██████╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║   ██║╚══██╔══╝██║   ██║██╔══██╗██╔═══██╗
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝█████╗  ██║   ██║   ██║   ██║   ██║██████╔╝██║   ██║
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══╝  ██║   ██║   ██║   ██║   ██║██╔══██╗██║   ██║
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║     ╚██████╔╝   ██║   ╚██████╔╝██║  ██║╚██████╔╝
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝

BANNER

echo -e "${C_PURPLE}${C_BOLD}  Aprende tecnología al revés.${C_RESET}"
echo -e "${C_DIM}  Learn tech backwards. · Apprends la tech à l'envers.${C_RESET}"
echo
echo -e "${C_CYAN}  Bienvenido a tu Codespace. Todo está listo: Python, Git, SQLite, curl.${C_RESET}"
echo -e "${C_DIM}  Welcome to your Codespace. Everything is ready: Python, Git, SQLite, curl.${C_RESET}"
echo
echo -e "${C_GREEN}  Para empezar / To start / Pour commencer:${C_RESET}"
echo
echo -e "    ${C_YELLOW}cd curriculum${C_RESET}"
echo -e "    ${C_YELLOW}./cf start${C_RESET}      ${C_DIM}# empezar la primera lección / start the first lesson${C_RESET}"
echo
echo -e "${C_PINK}  Comandos del runner / Runner commands:${C_RESET}"
echo -e "    ${C_DIM}./cf list        — ver todas las lecciones / list all lessons${C_RESET}"
echo -e "    ${C_DIM}./cf start [n]   — empezar una lección / start a lesson${C_RESET}"
echo -e "    ${C_DIM}./cf check       — validar la lección actual / check current lesson${C_RESET}"
echo -e "    ${C_DIM}./cf next        — pasar a la siguiente / go to next lesson${C_RESET}"
echo -e "    ${C_DIM}./cf progress    — ver tu progreso / show progress${C_RESET}"
echo -e "    ${C_DIM}./cf help        — ayuda / help${C_RESET}"
echo
