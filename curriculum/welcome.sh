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

echo -e "${C_PURPLE}${C_BOLD}  Aprenda tecnologia de trás para frente.${C_RESET}"
echo -e "${C_DIM}  Aprende tecnología al revés. · Learn tech backwards. · Apprends la tech à l'envers.${C_RESET}"
echo
echo -e "${C_CYAN}  Bem-vindo ao seu Codespace. Tudo pronto: Python, Git, SQLite, curl.${C_RESET}"
echo -e "${C_DIM}  Everything ready: Python, Git, SQLite, curl.${C_RESET}"
echo
echo -e "${C_GREEN}  Para começar / Para empezar / To start / Pour commencer :${C_RESET}"
echo
echo -e "    ${C_YELLOW}cd curriculum${C_RESET}"
echo -e "    ${C_YELLOW}./cf start${C_RESET}      ${C_DIM}# começa a primeira lição${C_RESET}"
echo
echo -e "${C_PINK}  Comandos do runner:${C_RESET}"
echo -e "    ${C_DIM}./cf list        — lista todas as lições${C_RESET}"
echo -e "    ${C_DIM}./cf start [n]   — começa uma lição${C_RESET}"
echo -e "    ${C_DIM}./cf check       — valida a lição atual${C_RESET}"
echo -e "    ${C_DIM}./cf next        — vai para a próxima lição${C_RESET}"
echo -e "    ${C_DIM}./cf progress    — seu progresso${C_RESET}"
echo -e "    ${C_DIM}./cf help        — ajuda completa${C_RESET}"
echo
echo -e "${C_DIM}  Outro idioma? export CF_LANG=es  (espanhol disponível)${C_RESET}"
echo
