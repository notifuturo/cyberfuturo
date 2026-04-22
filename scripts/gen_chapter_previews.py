#!/usr/bin/env python3
"""Generate chapters 02-08 locked-preview pages in all 4 languages.

Why a script (vs hand-authored HTML):
  - 7 chapters × 4 languages = 28 nearly-identical files
  - Hand editing would drift: emoji inconsistencies, stale slugs, broken
    hreflang chains, missing meta tags
  - Single source of truth for chapter metadata + per-language copy
  - Re-runnable: when a preview needs refinement, update CHAPTERS below and
    `python3 scripts/gen_chapter_previews.py` writes the 28 files

Output: site/{pt/curso,es/curso,en/course,fr/cours}/NN-slug/index.html

Fits ADR-0002 (stdlib-only Python). Zero dependencies. Idempotent.

Chapter 00 (full sample) and chapter 01 (substantive preview) are authored
by hand — do not overwrite those. This script only writes 02-08.
"""

from __future__ import annotations

import sys
from pathlib import Path
from string import Template

# ---------------------------------------------------------------------------
# Chapter catalog — slug, minutes, and per-language display fields.
# ---------------------------------------------------------------------------

LANGS = ["pt", "es", "en", "fr"]

# Path segment per language for the course container.
COURSE_DIR = {"pt": "curso", "es": "curso", "en": "course", "fr": "cours"}
BUY_PATH   = {"pt": "/pt/comprar/", "es": "/es/comprar/", "en": "/en/buy/", "fr": "/fr/acheter/"}
LOCALE     = {"pt": "pt-BR", "es": "es-419", "en": "en-US", "fr": "fr-CA"}
OG_LOCALE  = {"pt": "pt_BR", "es": "es_419", "en": "en_US", "fr": "fr_CA"}

# Shared chrome labels per language.
LABELS = {
    "pt": {
        "skip":"Pular para o conteúdo", "toc_open":"Abrir índice",
        "index":"ÍNDICE", "course_index":"ÍNDICE DO CURSO",
        "course_root":"curso/", "preview":"prévia", "reading":"● lendo",
        "free_sample":"✓ grátis", "unlock_heading":"DESBLOQUEIE 8 CAPÍTULOS",
        "unlock_price_note":"/ R$47 · única", "unlock_cta":"Comprar acesso",
        "buy_tiny":"Comprar · $9", "eye_num":"CAPÍTULO",
        "eye_paid_preview":"CAPÍTULO PAGO · PRÉVIA",
        "banner_line_a":"Você está lendo uma", "banner_strong":"prévia",
        "banner_line_b":"do capítulo", "banner_line_c":"Continue o curso inteiro por",
        "banner_price":"$9 USD", "banner_tail":"— pagamento único, acesso vitalício, 4 idiomas.",
        "banner_cta":"Comprar agora",
        "end_title":"FIM DA PRÉVIA", "end_lead":"Este capítulo continua com:",
        "end_cta":"Desbloquear capítulo inteiro · $9",
        "prev":"← CAPÍTULO ANTERIOR", "next":"DESBLOQUEAR PRÓXIMO →",
        "sidecar_live":"AO VIVO · CODESPACE",
        "sidecar_tab_exercise":"exercício", "sidecar_tab_history":"histórico", "sidecar_tab_hint":"dica",
        "sidecar_open":"Abrir em Codespaces ↗",
        "sidecar_task_title":"// tarefa (do repo público)",
        "sidecar_hint_tail_a":"O exercício é grátis:", "sidecar_hint_tail_b":"veja o task.md no GitHub",
        "sidecar_hint_tail_c":"A explicação — os porquês, o modelo mental, os atalhos — é o que o curso vende.",
        "sidecar_select":"Selecionar idioma",
        "footer_brand_tag":"— aprenda tecnologia de trás para frente.",
        "footer_home":"Início", "footer_course":"Curso", "footer_buy":"Comprar", "footer_privacy":"Privacidade",
        "drawer_close":"Fechar ✕", "drawer_aria":"Índice (móvel)",
        "preview_eyebrow":"O que você vai entender",
        "pill_stdlib":"stdlib apenas", "pill_nobuild":"sem build step",
        "pill_works":"funciona em 2036", "pill_4lang":"4 idiomas",
        "pill_9chap":"9 capítulos", "pill_modules":"3 módulos + 1 final",
        "pill_price":"$9 única · vitalício", "pill_nomonthly":"sem mensalidade",
    },
    "es": {
        "skip":"Saltar al contenido", "toc_open":"Abrir índice",
        "index":"ÍNDICE", "course_index":"ÍNDICE DEL CURSO",
        "course_root":"curso/", "preview":"muestra", "reading":"● leyendo",
        "free_sample":"✓ gratis", "unlock_heading":"DESBLOQUEA 8 CAPÍTULOS",
        "unlock_price_note":"/ una vez", "unlock_cta":"Comprar acceso",
        "buy_tiny":"Comprar · $9", "eye_num":"CAPÍTULO",
        "eye_paid_preview":"CAPÍTULO PAGO · MUESTRA",
        "banner_line_a":"Estás leyendo una", "banner_strong":"muestra",
        "banner_line_b":"del capítulo", "banner_line_c":"Continúa el curso completo por",
        "banner_price":"$9 USD", "banner_tail":"— una vez, acceso vitalicio, 4 idiomas.",
        "banner_cta":"Comprar ahora",
        "end_title":"FIN DE LA MUESTRA", "end_lead":"Este capítulo continúa con:",
        "end_cta":"Desbloquear capítulo completo · $9",
        "prev":"← CAPÍTULO ANTERIOR", "next":"DESBLOQUEAR SIGUIENTE →",
        "sidecar_live":"EN VIVO · CODESPACE",
        "sidecar_tab_exercise":"ejercicio", "sidecar_tab_history":"historial", "sidecar_tab_hint":"pista",
        "sidecar_open":"Abrir en Codespaces ↗",
        "sidecar_task_title":"// tarea (del repo público)",
        "sidecar_hint_tail_a":"El ejercicio es gratis:", "sidecar_hint_tail_b":"ve el task.md en GitHub",
        "sidecar_hint_tail_c":"La explicación — los porqués, el modelo mental, los atajos — es lo que vende el curso.",
        "sidecar_select":"Seleccionar idioma",
        "footer_brand_tag":"— aprende tecnología al revés.",
        "footer_home":"Inicio", "footer_course":"Curso", "footer_buy":"Comprar", "footer_privacy":"Privacidad",
        "drawer_close":"Cerrar ✕", "drawer_aria":"Índice (móvil)",
        "preview_eyebrow":"Lo que vas a entender",
        "pill_stdlib":"solo stdlib", "pill_nobuild":"sin build step",
        "pill_works":"funciona en 2036", "pill_4lang":"4 idiomas",
        "pill_9chap":"9 capítulos", "pill_modules":"3 módulos + 1 final",
        "pill_price":"$9 una vez · vitalicio", "pill_nomonthly":"sin suscripción",
    },
    "en": {
        "skip":"Skip to content", "toc_open":"Open index",
        "index":"INDEX", "course_index":"COURSE INDEX",
        "course_root":"course/", "preview":"preview", "reading":"● reading",
        "free_sample":"✓ free", "unlock_heading":"UNLOCK 8 CHAPTERS",
        "unlock_price_note":"/ one-time", "unlock_cta":"Buy access",
        "buy_tiny":"Buy · $9", "eye_num":"CHAPTER",
        "eye_paid_preview":"PAID CHAPTER · PREVIEW",
        "banner_line_a":"You're reading a", "banner_strong":"preview",
        "banner_line_b":"of chapter", "banner_line_c":"Continue the full course for",
        "banner_price":"$9 USD", "banner_tail":"— one-time, lifetime access, 4 languages.",
        "banner_cta":"Buy now",
        "end_title":"END OF PREVIEW", "end_lead":"This chapter continues with:",
        "end_cta":"Unlock full chapter · $9",
        "prev":"← PREVIOUS CHAPTER", "next":"UNLOCK NEXT →",
        "sidecar_live":"LIVE · CODESPACE",
        "sidecar_tab_exercise":"exercise", "sidecar_tab_history":"history", "sidecar_tab_hint":"hint",
        "sidecar_open":"Open in Codespaces ↗",
        "sidecar_task_title":"// task (from the public repo)",
        "sidecar_hint_tail_a":"The exercise is free:", "sidecar_hint_tail_b":"see task.md on GitHub",
        "sidecar_hint_tail_c":"The explanation — the why, the mental model, the shortcuts — is what the course sells.",
        "sidecar_select":"Select language",
        "footer_brand_tag":"— learn tech backwards.",
        "footer_home":"Home", "footer_course":"Course", "footer_buy":"Buy", "footer_privacy":"Privacy",
        "drawer_close":"Close ✕", "drawer_aria":"Index (mobile)",
        "preview_eyebrow":"What you'll understand",
        "pill_stdlib":"stdlib only", "pill_nobuild":"no build step",
        "pill_works":"works in 2036", "pill_4lang":"4 languages",
        "pill_9chap":"9 chapters", "pill_modules":"3 modules + 1 final",
        "pill_price":"$9 once · lifetime", "pill_nomonthly":"no subscription",
    },
    "fr": {
        "skip":"Aller au contenu", "toc_open":"Ouvrir l'index",
        "index":"INDEX", "course_index":"INDEX DU COURS",
        "course_root":"cours/", "preview":"extrait", "reading":"● lecture",
        "free_sample":"✓ gratuit", "unlock_heading":"DÉBLOQUE 8 CHAPITRES",
        "unlock_price_note":"/ unique", "unlock_cta":"Acheter l'accès",
        "buy_tiny":"Acheter · 9 $", "eye_num":"CHAPITRE",
        "eye_paid_preview":"CHAPITRE PAYANT · EXTRAIT",
        "banner_line_a":"Tu lis un", "banner_strong":"extrait",
        "banner_line_b":"du chapitre", "banner_line_c":"Continue le cours entier pour",
        "banner_price":"9 $ USD", "banner_tail":"— paiement unique, accès à vie, 4 langues.",
        "banner_cta":"Acheter maintenant",
        "end_title":"FIN DE L'EXTRAIT", "end_lead":"Ce chapitre continue avec :",
        "end_cta":"Débloquer le chapitre entier · 9 $",
        "prev":"← CHAPITRE PRÉCÉDENT", "next":"DÉBLOQUER LE SUIVANT →",
        "sidecar_live":"EN DIRECT · CODESPACE",
        "sidecar_tab_exercise":"exercice", "sidecar_tab_history":"historique", "sidecar_tab_hint":"indice",
        "sidecar_open":"Ouvrir dans Codespaces ↗",
        "sidecar_task_title":"// tâche (du dépôt public)",
        "sidecar_hint_tail_a":"L'exercice est gratuit :", "sidecar_hint_tail_b":"vois le task.md sur GitHub",
        "sidecar_hint_tail_c":"L'explication — le pourquoi, le modèle mental, les raccourcis — est ce que le cours vend.",
        "sidecar_select":"Choisir la langue",
        "footer_brand_tag":"— apprends la tech à l'envers.",
        "footer_home":"Accueil", "footer_course":"Cours", "footer_buy":"Acheter", "footer_privacy":"Confidentialité",
        "drawer_close":"Fermer ✕", "drawer_aria":"Index (mobile)",
        "preview_eyebrow":"Ce que tu vas comprendre",
        "pill_stdlib":"stdlib uniquement", "pill_nobuild":"pas de build step",
        "pill_works":"fonctionne en 2036", "pill_4lang":"4 langues",
        "pill_9chap":"9 chapitres", "pill_modules":"3 modules + 1 final",
        "pill_price":"9 $ unique · à vie", "pill_nomonthly":"pas d'abonnement",
    },
}

# Full 9-chapter catalog (so TOC rendering is correct on every preview page).
# Chapters 00 + 01 are authored elsewhere; this script reads their metadata
# only to render the sidebar correctly.
CHAPTERS = [
    {"n":0, "slug":"00-bienvenido", "mins":8,  "state":"sample",
     "titles":{"pt":"Boas-vindas", "es":"Bienvenida", "en":"Welcome", "fr":"Bienvenue"}},
    {"n":1, "slug":"01-terminal", "mins":14, "state":"preview",
     "titles":{"pt":"Terminal como linguagem", "es":"Terminal como lenguaje",
               "en":"The terminal as a language", "fr":"Terminal comme langage"}},
    {"n":2, "slug":"02-primer-git-commit", "mins":18, "state":"locked",
     "titles":{"pt":"Seu primeiro commit em Git", "es":"Tu primer commit en Git",
               "en":"Your first Git commit", "fr":"Ton premier commit Git"}},
    {"n":3, "slug":"03-python-hola", "mins":12, "state":"locked",
     "titles":{"pt":"Python: olá, mundo", "es":"Python: hola, mundo",
               "en":"Python: hello, world", "fr":"Python : bonjour, monde"}},
    {"n":4, "slug":"04-ramos-git", "mins":22, "state":"locked",
     "titles":{"pt":"Ramos e histórias paralelas", "es":"Ramas e historias paralelas",
               "en":"Branches and parallel histories", "fr":"Branches et histoires parallèles"}},
    {"n":5, "slug":"05-primera-sql", "mins":20, "state":"locked",
     "titles":{"pt":"Sua primeira consulta SQL", "es":"Tu primera consulta SQL",
               "en":"Your first SQL query", "fr":"Ta première requête SQL"}},
    {"n":6, "slug":"06-http-apis", "mins":24, "state":"locked",
     "titles":{"pt":"HTTP: como a web conversa", "es":"HTTP: cómo conversa la web",
               "en":"HTTP: how the web talks", "fr":"HTTP : comment le web parle"}},
    {"n":7, "slug":"07-loops-dados", "mins":18, "state":"locked",
     "titles":{"pt":"Loops e coleções de dados", "es":"Loops y colecciones de datos",
               "en":"Loops and data collections", "fr":"Boucles et collections de données"}},
    {"n":8, "slug":"08-dicionarios", "mins":20, "state":"locked",
     "titles":{"pt":"Dicionários e o mundo real", "es":"Diccionarios y el mundo real",
               "en":"Dictionaries and the real world", "fr":"Dictionnaires et le monde réel"}},
]

# Per-chapter preview content — intro lead + 3 "what you'll understand" bullets
# + 3 "continues with" bullets. These are terse by design: the preview pitch
# is the teaching's value prop, not the teaching itself. Chapters 02-08 only.
PREVIEW = {
    2: {
        "pt": {
            "lead":"Todo trabalho de verdade acaba no Git. Neste capítulo você vai sair do 'copiei o arquivo para outra pasta pra salvar uma versão' e entrar no modelo mental certo: o Git é uma linha do tempo e cada commit é um ponto nela.",
            "will":["Por que <code class='cf-code'>git init</code> cria uma pasta invisível chamada <code class='cf-code'>.git</code>",
                    "O que <code class='cf-code'>git add</code> faz que <code class='cf-code'>git commit</code> não faz (e vice-versa)",
                    "Como escrever uma mensagem de commit que seu eu-do-futuro não vai odiar"],
            "cont":["a anatomia de um commit por dentro (hash, árvore, autor, timestamp)",
                    "a diferença prática entre <code class='cf-code'>git add</code> e <code class='cf-code'>git add -p</code>",
                    "as três formas de desfazer (e qual você vai usar 95% das vezes)"],
        },
        "es": {
            "lead":"Todo trabajo de verdad termina en Git. En este capítulo vas a salir del 'copié el archivo a otra carpeta para guardar una versión' y entrar al modelo mental correcto: Git es una línea de tiempo y cada commit es un punto en ella.",
            "will":["Por qué <code class='cf-code'>git init</code> crea una carpeta invisible llamada <code class='cf-code'>.git</code>",
                    "Lo que <code class='cf-code'>git add</code> hace que <code class='cf-code'>git commit</code> no hace (y viceversa)",
                    "Cómo escribir un mensaje de commit que tu yo del futuro no va a odiar"],
            "cont":["la anatomía de un commit por dentro (hash, árbol, autor, timestamp)",
                    "la diferencia práctica entre <code class='cf-code'>git add</code> y <code class='cf-code'>git add -p</code>",
                    "las tres formas de deshacer (y cuál vas a usar el 95% de las veces)"],
        },
        "en": {
            "lead":"All real work ends up in Git. This chapter moves you from 'I copied the file to another folder to save a version' to the right mental model: Git is a timeline and every commit is a point on it.",
            "will":["Why <code class='cf-code'>git init</code> creates an invisible folder called <code class='cf-code'>.git</code>",
                    "What <code class='cf-code'>git add</code> does that <code class='cf-code'>git commit</code> doesn't (and vice versa)",
                    "How to write a commit message your future self won't hate"],
            "cont":["the anatomy of a commit under the hood (hash, tree, author, timestamp)",
                    "the practical difference between <code class='cf-code'>git add</code> and <code class='cf-code'>git add -p</code>",
                    "the three ways to undo (and which one you'll use 95% of the time)"],
        },
        "fr": {
            "lead":"Tout vrai travail finit dans Git. Ce chapitre te fait passer de « j'ai copié le fichier dans un autre dossier pour sauvegarder une version » au bon modèle mental : Git est une ligne du temps et chaque commit est un point dessus.",
            "will":["Pourquoi <code class='cf-code'>git init</code> crée un dossier invisible appelé <code class='cf-code'>.git</code>",
                    "Ce que <code class='cf-code'>git add</code> fait que <code class='cf-code'>git commit</code> ne fait pas (et inversement)",
                    "Comment écrire un message de commit que ton toi-du-futur ne va pas haïr"],
            "cont":["l'anatomie d'un commit sous le capot (hash, arbre, auteur, timestamp)",
                    "la différence pratique entre <code class='cf-code'>git add</code> et <code class='cf-code'>git add -p</code>",
                    "les trois façons de défaire (et celle que tu vas utiliser 95 % du temps)"],
        },
    },
    3: {
        "pt": {
            "lead":"Python não é uma linguagem misteriosa. É uma ferramenta que executa instruções linha por linha. Se você já escreveu um comando no terminal, já sabe 30% de Python.",
            "will":["A diferença entre rodar Python no REPL e rodar um arquivo <code class='cf-code'>.py</code>",
                    "Por que <code class='cf-code'>print()</code> tem parênteses em Python 3 (e não em Python 2)",
                    "Quando usar <code class='cf-code'>input()</code> e quando nunca usar"],
            "cont":["variáveis, tipos (<code class='cf-code'>str</code>, <code class='cf-code'>int</code>, <code class='cf-code'>float</code>) e o perigo de misturar",
                    "funções: o que é um argumento, um retorno, e uma função sem retorno",
                    "como ler um script de outra pessoa e entender o fluxo em 30 segundos"],
        },
        "es": {
            "lead":"Python no es un lenguaje misterioso. Es una herramienta que ejecuta instrucciones línea por línea. Si ya escribiste un comando en la terminal, ya sabes el 30% de Python.",
            "will":["La diferencia entre ejecutar Python en el REPL y ejecutar un archivo <code class='cf-code'>.py</code>",
                    "Por qué <code class='cf-code'>print()</code> tiene paréntesis en Python 3 (y no en Python 2)",
                    "Cuándo usar <code class='cf-code'>input()</code> y cuándo no usarlo nunca"],
            "cont":["variables, tipos (<code class='cf-code'>str</code>, <code class='cf-code'>int</code>, <code class='cf-code'>float</code>) y el peligro de mezclarlos",
                    "funciones: qué es un argumento, un retorno, y una función sin retorno",
                    "cómo leer un script de otra persona y entender el flujo en 30 segundos"],
        },
        "en": {
            "lead":"Python isn't a mysterious language. It's a tool that runs instructions line by line. If you've typed a command into a terminal, you already know 30% of Python.",
            "will":["The difference between running Python in the REPL and running a <code class='cf-code'>.py</code> file",
                    "Why <code class='cf-code'>print()</code> has parentheses in Python 3 (and not in Python 2)",
                    "When to use <code class='cf-code'>input()</code> and when to never use it"],
            "cont":["variables, types (<code class='cf-code'>str</code>, <code class='cf-code'>int</code>, <code class='cf-code'>float</code>) and the danger of mixing them",
                    "functions: what an argument is, what a return value is, what a function with no return does",
                    "how to read someone else's script and understand the flow in 30 seconds"],
        },
        "fr": {
            "lead":"Python n'est pas un langage mystérieux. C'est un outil qui exécute des instructions ligne par ligne. Si tu as déjà tapé une commande dans un terminal, tu connais déjà 30 % de Python.",
            "will":["La différence entre exécuter Python dans le REPL et exécuter un fichier <code class='cf-code'>.py</code>",
                    "Pourquoi <code class='cf-code'>print()</code> a des parenthèses en Python 3 (et pas en Python 2)",
                    "Quand utiliser <code class='cf-code'>input()</code> et quand ne jamais l'utiliser"],
            "cont":["variables, types (<code class='cf-code'>str</code>, <code class='cf-code'>int</code>, <code class='cf-code'>float</code>) et le danger de les mélanger",
                    "fonctions : ce qu'est un argument, un retour, une fonction sans retour",
                    "comment lire le script de quelqu'un d'autre et comprendre le flux en 30 secondes"],
        },
    },
    4: {
        "pt": {
            "lead":"Ramos em Git é como ter múltiplas cópias do projeto sem copiar nada. Cada ramo é uma linha do tempo paralela. Quando você está pronto, você funde duas linhas em uma.",
            "will":["Por que <code class='cf-code'>main</code> não é sagrado — é só um nome",
                    "A diferença entre <code class='cf-code'>git switch</code> e <code class='cf-code'>git checkout</code> (e por que <code class='cf-code'>switch</code> é novo)",
                    "O que é um fast-forward merge e quando ele acontece automaticamente"],
            "cont":["como o <code class='cf-code'>git log --graph</code> te mostra a topologia real do projeto",
                    "o que é um conflito de merge e as três perguntas que resolvem 90% deles",
                    "rebase: quando usar, quando não usar, e por que tanta gente tem opinião forte"],
        },
        "es": {
            "lead":"Las ramas en Git son como tener múltiples copias del proyecto sin copiar nada. Cada rama es una línea de tiempo paralela. Cuando estás listo, fusionas dos líneas en una.",
            "will":["Por qué <code class='cf-code'>main</code> no es sagrado — es solo un nombre",
                    "La diferencia entre <code class='cf-code'>git switch</code> y <code class='cf-code'>git checkout</code> (y por qué <code class='cf-code'>switch</code> es nuevo)",
                    "Qué es un fast-forward merge y cuándo ocurre automáticamente"],
            "cont":["cómo <code class='cf-code'>git log --graph</code> te muestra la topología real del proyecto",
                    "qué es un conflicto de merge y las tres preguntas que resuelven el 90%",
                    "rebase: cuándo usarlo, cuándo no, y por qué tanta gente tiene opinión fuerte"],
        },
        "en": {
            "lead":"Branches in Git are like having multiple copies of the project without copying anything. Each branch is a parallel timeline. When you're ready, you merge two timelines into one.",
            "will":["Why <code class='cf-code'>main</code> isn't sacred — it's just a name",
                    "The difference between <code class='cf-code'>git switch</code> and <code class='cf-code'>git checkout</code> (and why <code class='cf-code'>switch</code> is new)",
                    "What a fast-forward merge is and when it happens automatically"],
            "cont":["how <code class='cf-code'>git log --graph</code> shows you the project's real topology",
                    "what a merge conflict is and the three questions that resolve 90% of them",
                    "rebase: when to use it, when not to, and why everyone has strong opinions"],
        },
        "fr": {
            "lead":"Les branches Git, c'est comme avoir plusieurs copies du projet sans rien copier. Chaque branche est une ligne du temps parallèle. Quand tu es prêt, tu fusionnes deux lignes en une.",
            "will":["Pourquoi <code class='cf-code'>main</code> n'est pas sacré — c'est juste un nom",
                    "La différence entre <code class='cf-code'>git switch</code> et <code class='cf-code'>git checkout</code> (et pourquoi <code class='cf-code'>switch</code> est récent)",
                    "Ce qu'est un fast-forward merge et quand il se produit automatiquement"],
            "cont":["comment <code class='cf-code'>git log --graph</code> te montre la topologie réelle du projet",
                    "ce qu'est un conflit de merge et les trois questions qui en résolvent 90 %",
                    "rebase : quand l'utiliser, quand ne pas l'utiliser, et pourquoi tout le monde a un avis tranché"],
        },
    },
    5: {
        "pt": {
            "lead":"SQL é uma linguagem de perguntar a dados. Você descreve o que quer, não como achar. O banco resolve. Depois de aprender SQL, você vai ver dados em todo lugar onde antes via caos.",
            "will":["Por que tabelas têm colunas tipadas (e o que acontece quando você ignora os tipos)",
                    "A diferença entre <code class='cf-code'>SELECT *</code> e <code class='cf-code'>SELECT id, name</code> — e qual sua chefe vai preferir",
                    "Como <code class='cf-code'>WHERE</code> filtra e por que a ordem dos filtros importa pra performance"],
            "cont":["<code class='cf-code'>JOIN</code>: os 4 tipos que existem, e os 2 que você vai usar de verdade",
                    "agregações: <code class='cf-code'>COUNT</code>, <code class='cf-code'>GROUP BY</code>, <code class='cf-code'>HAVING</code> — quando cada um entra",
                    "índices: o que são, por que existem, e por que uma query lenta quase sempre tem culpa deles"],
        },
        "es": {
            "lead":"SQL es un lenguaje para hacerle preguntas a los datos. Describes lo que quieres, no cómo encontrarlo. La base de datos resuelve. Después de aprender SQL, vas a ver datos en todos lados donde antes veías caos.",
            "will":["Por qué las tablas tienen columnas con tipos (y lo que pasa cuando ignoras los tipos)",
                    "La diferencia entre <code class='cf-code'>SELECT *</code> y <code class='cf-code'>SELECT id, name</code> — y cuál va a preferir tu jefa",
                    "Cómo <code class='cf-code'>WHERE</code> filtra y por qué el orden de los filtros importa para el rendimiento"],
            "cont":["<code class='cf-code'>JOIN</code>: los 4 tipos que existen, y los 2 que vas a usar de verdad",
                    "agregaciones: <code class='cf-code'>COUNT</code>, <code class='cf-code'>GROUP BY</code>, <code class='cf-code'>HAVING</code> — cuándo entra cada uno",
                    "índices: qué son, por qué existen, y por qué una query lenta casi siempre tiene culpa de ellos"],
        },
        "en": {
            "lead":"SQL is a language for asking questions of data. You describe what you want, not how to find it. The database solves it. After you learn SQL, you start seeing data everywhere you used to see chaos.",
            "will":["Why tables have typed columns (and what happens when you ignore the types)",
                    "The difference between <code class='cf-code'>SELECT *</code> and <code class='cf-code'>SELECT id, name</code> — and which your tech lead will prefer",
                    "How <code class='cf-code'>WHERE</code> filters and why the order of filters matters for performance"],
            "cont":["<code class='cf-code'>JOIN</code>: the 4 kinds that exist, and the 2 you'll actually use",
                    "aggregations: <code class='cf-code'>COUNT</code>, <code class='cf-code'>GROUP BY</code>, <code class='cf-code'>HAVING</code> — when each comes in",
                    "indexes: what they are, why they exist, and why a slow query almost always has them to blame"],
        },
        "fr": {
            "lead":"SQL est un langage pour poser des questions aux données. Tu décris ce que tu veux, pas comment le trouver. La base de données s'en charge. Après avoir appris SQL, tu vois des données partout où tu voyais du chaos avant.",
            "will":["Pourquoi les tables ont des colonnes typées (et ce qui arrive quand tu ignores les types)",
                    "La différence entre <code class='cf-code'>SELECT *</code> et <code class='cf-code'>SELECT id, name</code> — et lequel ta tech lead préfère",
                    "Comment <code class='cf-code'>WHERE</code> filtre et pourquoi l'ordre des filtres compte pour la performance"],
            "cont":["<code class='cf-code'>JOIN</code> : les 4 types existants, et les 2 que tu vas vraiment utiliser",
                    "agrégations : <code class='cf-code'>COUNT</code>, <code class='cf-code'>GROUP BY</code>, <code class='cf-code'>HAVING</code> — quand chacun intervient",
                    "les index : ce qu'ils sont, pourquoi ils existent, et pourquoi une requête lente a presque toujours un index en cause"],
        },
    },
    6: {
        "pt": {
            "lead":"Quase toda aplicação moderna conversa por HTTP. Depois desse capítulo, quando alguém falar 'a API tá retornando 401', você vai saber exatamente o que aconteceu e onde olhar.",
            "will":["Por que HTTP tem verbos (GET, POST, PUT, DELETE) — e o que cada um significa de verdade",
                    "O que os status codes contam (200, 301, 404, 500) e como ler um <em>header</em>",
                    "A diferença entre uma URL que serve HTML e uma que serve JSON"],
            "cont":["como <code class='cf-code'>curl</code> te deixa falar com qualquer API pública",
                    "autenticação: <em>API keys</em>, <em>bearer tokens</em>, e por que nada disso é segurança real sem HTTPS",
                    "erros que parecem rede mas são código (CORS, timeout, payload grande demais)"],
        },
        "es": {
            "lead":"Casi toda aplicación moderna conversa por HTTP. Después de este capítulo, cuando alguien diga 'la API está devolviendo 401', vas a saber exactamente qué pasó y dónde mirar.",
            "will":["Por qué HTTP tiene verbos (GET, POST, PUT, DELETE) — y qué significa cada uno de verdad",
                    "Lo que cuentan los status codes (200, 301, 404, 500) y cómo leer un <em>header</em>",
                    "La diferencia entre una URL que sirve HTML y una que sirve JSON"],
            "cont":["cómo <code class='cf-code'>curl</code> te deja hablar con cualquier API pública",
                    "autenticación: <em>API keys</em>, <em>bearer tokens</em>, y por qué nada de eso es seguridad real sin HTTPS",
                    "errores que parecen de red pero son de código (CORS, timeout, payload demasiado grande)"],
        },
        "en": {
            "lead":"Almost every modern app talks over HTTP. After this chapter, when someone says 'the API is returning 401,' you'll know exactly what happened and where to look.",
            "will":["Why HTTP has verbs (GET, POST, PUT, DELETE) — and what each really means",
                    "What status codes tell you (200, 301, 404, 500) and how to read a <em>header</em>",
                    "The difference between a URL that serves HTML and one that serves JSON"],
            "cont":["how <code class='cf-code'>curl</code> lets you talk to any public API",
                    "authentication: API keys, bearer tokens, and why none of that is real security without HTTPS",
                    "errors that look like network issues but are code issues (CORS, timeout, payload too large)"],
        },
        "fr": {
            "lead":"Presque toutes les apps modernes parlent en HTTP. Après ce chapitre, quand quelqu'un dit « l'API renvoie 401 », tu sauras exactement ce qui s'est passé et où regarder.",
            "will":["Pourquoi HTTP a des verbes (GET, POST, PUT, DELETE) — et ce que chacun veut vraiment dire",
                    "Ce que racontent les status codes (200, 301, 404, 500) et comment lire un <em>header</em>",
                    "La différence entre une URL qui sert du HTML et une qui sert du JSON"],
            "cont":["comment <code class='cf-code'>curl</code> te laisse parler à n'importe quelle API publique",
                    "authentification : API keys, bearer tokens, et pourquoi rien de tout ça n'est de la vraie sécurité sans HTTPS",
                    "des erreurs qui ressemblent à du réseau mais sont du code (CORS, timeout, payload trop gros)"],
        },
    },
    7: {
        "pt": {
            "lead":"Um loop é a ferramenta mais básica de programação, e a que mais gente usa errado. Neste capítulo você vai aprender a iterar com intenção — não repetindo código, iterando sobre dados.",
            "will":["A diferença entre <code class='cf-code'>for</code> e <code class='cf-code'>while</code> — e quando um é mais claro que o outro",
                    "Por que <code class='cf-code'>range()</code> existe (e por que você raramente deveria precisar dele)",
                    "O que significa iterar sobre uma lista, um arquivo ou o JSON que veio da API"],
            "cont":["<em>list comprehensions</em>: a sintaxe que troca 4 linhas por 1, e quando NÃO usar",
                    "<code class='cf-code'>enumerate</code> e <code class='cf-code'>zip</code>: os dois ajudantes que resolvem 80% dos loops do dia-a-dia",
                    "o padrão 'leia linha por linha sem carregar o arquivo inteiro na memória'"],
        },
        "es": {
            "lead":"Un loop es la herramienta más básica de programación, y la que más gente usa mal. En este capítulo vas a aprender a iterar con intención — no repitiendo código, iterando sobre datos.",
            "will":["La diferencia entre <code class='cf-code'>for</code> y <code class='cf-code'>while</code> — y cuándo uno es más claro que el otro",
                    "Por qué existe <code class='cf-code'>range()</code> (y por qué rara vez deberías necesitarlo)",
                    "Qué significa iterar sobre una lista, un archivo o el JSON que vino de la API"],
            "cont":["<em>list comprehensions</em>: la sintaxis que cambia 4 líneas por 1, y cuándo NO usarla",
                    "<code class='cf-code'>enumerate</code> y <code class='cf-code'>zip</code>: los dos ayudantes que resuelven el 80% de los loops del día a día",
                    "el patrón 'lee línea por línea sin cargar el archivo entero en memoria'"],
        },
        "en": {
            "lead":"A loop is programming's most basic tool, and the one most people use wrong. In this chapter you'll learn to iterate with intent — not by repeating code, but by iterating over data.",
            "will":["The difference between <code class='cf-code'>for</code> and <code class='cf-code'>while</code> — and when each is clearer than the other",
                    "Why <code class='cf-code'>range()</code> exists (and why you should rarely need it)",
                    "What it means to iterate over a list, a file, or the JSON that came from the API"],
            "cont":["list comprehensions: the syntax that replaces 4 lines with 1, and when NOT to reach for it",
                    "<code class='cf-code'>enumerate</code> and <code class='cf-code'>zip</code>: the two helpers that solve 80% of daily loops",
                    "the 'read line by line without loading the whole file into memory' pattern"],
        },
        "fr": {
            "lead":"Une boucle est l'outil le plus basique de la programmation, et celui que le plus de gens utilisent mal. Dans ce chapitre tu vas apprendre à itérer avec intention — pas en répétant du code, mais en itérant sur des données.",
            "will":["La différence entre <code class='cf-code'>for</code> et <code class='cf-code'>while</code> — et quand l'un est plus clair que l'autre",
                    "Pourquoi <code class='cf-code'>range()</code> existe (et pourquoi tu en auras rarement besoin)",
                    "Ce que veut dire itérer sur une liste, un fichier, ou le JSON reçu de l'API"],
            "cont":["les <em>list comprehensions</em> : la syntaxe qui remplace 4 lignes par 1, et quand NE PAS l'utiliser",
                    "<code class='cf-code'>enumerate</code> et <code class='cf-code'>zip</code> : les deux aides qui résolvent 80 % des boucles du quotidien",
                    "le pattern « lis ligne par ligne sans charger tout le fichier en mémoire »"],
        },
    },
    8: {
        "pt": {
            "lead":"Dicionários são o tipo de dado mais importante de Python. Se você entender um <code class='cf-code'>dict</code> profundamente, você entende o modelo mental por trás de 90% das APIs modernas.",
            "will":["Por que um <code class='cf-code'>dict</code> é 10.000× mais rápido que uma lista pra buscar por chave",
                    "A diferença entre <code class='cf-code'>d['x']</code> e <code class='cf-code'>d.get('x')</code> — e por que o segundo quase sempre é mais seguro",
                    "Como dicionários aninhados representam JSON (e vice-versa)"],
            "cont":["o padrão 'agrupe por uma chave e conte' que aparece em toda análise de dados",
                    "<code class='cf-code'>collections.Counter</code> e <code class='cf-code'>defaultdict</code>: quando vale a pena sair do <code class='cf-code'>dict</code> puro",
                    "como um loop sobre um <code class='cf-code'>dict</code> é diferente de um loop sobre uma lista — e o que isso diz sobre o que você quer"],
        },
        "es": {
            "lead":"Los diccionarios son el tipo de dato más importante de Python. Si entiendes un <code class='cf-code'>dict</code> a fondo, entiendes el modelo mental detrás del 90% de las APIs modernas.",
            "will":["Por qué un <code class='cf-code'>dict</code> es 10.000× más rápido que una lista para buscar por clave",
                    "La diferencia entre <code class='cf-code'>d['x']</code> y <code class='cf-code'>d.get('x')</code> — y por qué el segundo casi siempre es más seguro",
                    "Cómo los diccionarios anidados representan JSON (y viceversa)"],
            "cont":["el patrón 'agrupa por una clave y cuenta' que aparece en todo análisis de datos",
                    "<code class='cf-code'>collections.Counter</code> y <code class='cf-code'>defaultdict</code>: cuándo vale la pena salir del <code class='cf-code'>dict</code> puro",
                    "cómo un loop sobre un <code class='cf-code'>dict</code> es diferente de un loop sobre una lista — y qué dice eso sobre lo que quieres"],
        },
        "en": {
            "lead":"Dictionaries are Python's most important data type. If you understand a <code class='cf-code'>dict</code> deeply, you understand the mental model behind 90% of modern APIs.",
            "will":["Why a <code class='cf-code'>dict</code> is 10,000× faster than a list for key lookups",
                    "The difference between <code class='cf-code'>d['x']</code> and <code class='cf-code'>d.get('x')</code> — and why the second is almost always safer",
                    "How nested dictionaries represent JSON (and vice versa)"],
            "cont":["the 'group by a key and count' pattern that shows up in every data-analysis task",
                    "<code class='cf-code'>collections.Counter</code> and <code class='cf-code'>defaultdict</code>: when it's worth leaving plain <code class='cf-code'>dict</code>",
                    "how iterating over a <code class='cf-code'>dict</code> differs from iterating over a list — and what that says about what you want"],
        },
        "fr": {
            "lead":"Les dictionnaires sont le type de données le plus important de Python. Si tu comprends un <code class='cf-code'>dict</code> en profondeur, tu comprends le modèle mental derrière 90 % des APIs modernes.",
            "will":["Pourquoi un <code class='cf-code'>dict</code> est 10 000× plus rapide qu'une liste pour chercher par clé",
                    "La différence entre <code class='cf-code'>d['x']</code> et <code class='cf-code'>d.get('x')</code> — et pourquoi le second est presque toujours plus sûr",
                    "Comment les dictionnaires imbriqués représentent du JSON (et inversement)"],
            "cont":["le pattern « regroupe par une clé et compte » qui apparaît dans toute analyse de données",
                    "<code class='cf-code'>collections.Counter</code> et <code class='cf-code'>defaultdict</code> : quand ça vaut la peine de sortir du <code class='cf-code'>dict</code> pur",
                    "comment itérer sur un <code class='cf-code'>dict</code> diffère d'itérer sur une liste — et ce que ça dit sur ce que tu veux"],
        },
    },
}


# ---------------------------------------------------------------------------
# Template body. Uses $identifier placeholders (string.Template semantics)
# so curly braces inside HTML stay literal.
# ---------------------------------------------------------------------------

TPL = Template("""<!doctype html>
<html lang="$locale">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$title — $preview_word · CyberFuturo</title>
  <meta name="description" content="$meta_desc">
  <meta property="og:title" content="CyberFuturo — $title ($preview_word)">
  <meta property="og:description" content="$og_desc">
  <meta property="og:type" content="article">
  <meta property="og:url" content="$self_url">
  <meta property="og:locale" content="$og_locale">
  <meta name="theme-color" content="#1e1e2e">
  <meta name="color-scheme" content="dark">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="canonical" href="$self_url">
  <link rel="alternate" hreflang="pt-BR" href="$pt_url">
  <link rel="alternate" hreflang="es-419" href="$es_url">
  <link rel="alternate" hreflang="en-US" href="$en_url">
  <link rel="alternate" hreflang="fr-CA" href="$fr_url">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>

<a class="skip-link" href="#main">$skip_text</a>

<div class="cf">
  <div class="cf-glow" aria-hidden="true"></div>
  <div class="cf-glow-pink" aria-hidden="true"></div>

  <header class="cf-header">
    <a class="cf-hamb" href="#toc" aria-label="$toc_open"><span class="cf-hamb-icon">≡</span> $index_text</a>
    <a class="cf-brand" href="/$lang/"><span class="p">&gt;_</span><span>Cyber<b>Futuro</b></span></a>
    <div class="cf-head-progress" aria-hidden="true">
      <span>CAP. $nn</span>
      <div class="track"><div class="fill" style="width: $progress%"></div></div>
      <span>$preview_word</span>
    </div>
    <div class="cf-head-right">
      <div class="lang-switcher" role="navigation" aria-label="$sidecar_select">
        <a href="$pt_url" hreflang="pt" data-lang="pt">PT</a>
        <a href="$es_url" hreflang="es" data-lang="es">ES</a>
        <a href="$en_url" hreflang="en" data-lang="en">EN</a>
        <a href="$fr_url" hreflang="fr" data-lang="fr">FR</a>
      </div>
      <a class="cf-btn cf-btn-tiny cf-btn-primary" href="$buy_path">$buy_tiny</a>
    </div>
  </header>

  <div class="cf-banner" role="note">
    <div class="cf-banner-text">
      <span class="cf-banner-lock">🔒</span>
      <span>$banner_line_a <strong>$banner_strong</strong> $banner_line_b $nn. $banner_line_c <span class="cf-banner-price">$banner_price</span> $banner_tail</span>
    </div>
    <div class="cf-banner-actions">
      <a class="cf-btn cf-btn-tiny cf-btn-primary" href="$buy_path">$banner_cta</a>
    </div>
  </div>

  <div class="cf-grid">

    <aside class="cf-side">
      <nav class="cf-toc" aria-label="$course_index">
        <div class="cf-toc-title">$course_index</div>
        <div class="cf-toc-root">$course_root</div>
        <ul class="cf-toc-tree">$toc_items</ul>
        <div class="cf-toc-unlock">
          <div class="cf-toc-unlock-label">$unlock_heading</div>
          <div class="cf-toc-unlock-price">$banner_price <span>$unlock_price_note</span></div>
          <a class="cf-btn cf-btn-primary" href="$buy_path" style="width: 100%; justify-content: center;">$unlock_cta</a>
        </div>
      </nav>
    </aside>

    <main class="cf-article" id="main">
      <div class="cf-eyebrow">
        <span class="e-num">$eye_num $nn</span>
        <span class="e-dot">·</span>
        <span>$mins min</span>
        <span class="e-dot">·</span>
        <span>$eye_paid_preview</span>
      </div>
      <h1 class="cf-chap-title">$title.</h1>
      <p class="cf-chap-lead">$lead</p>

      <div class="cf-prose">
        <section>
          <h2>$preview_eyebrow</h2>
          <ul style="padding-left: 22px; margin: 0 0 28px;">
            $will_bullets
          </ul>
        </section>
      </div>

      <aside class="cf-callout" style="margin-top: 32px; border-left-color: var(--accent); background: rgba(189,147,249,0.06);">
        <div class="cf-callout-mark" style="color: var(--accent);">🔒</div>
        <div>
          <div class="cf-callout-title" style="color: var(--accent);">$end_title</div>
          <div class="cf-callout-body" style="color: var(--text);">
            $end_lead
            <ul style="padding-left: 22px; margin: 12px 0 18px;">
              $cont_bullets
            </ul>
            <a class="cf-btn cf-btn-primary" href="$buy_path">$end_cta</a>
          </div>
        </div>
      </aside>

      <section class="cf-proof" style="margin-top: 32px;" aria-label="$course_index">
        <div class="cf-proof-pill tech"><span class="cf-proof-pill-icon">▸</span> $pill_stdlib</div>
        <div class="cf-proof-pill tech"><span class="cf-proof-pill-icon">▸</span> $pill_nobuild</div>
        <div class="cf-proof-pill tech"><span class="cf-proof-pill-icon">▸</span> $pill_works</div>
        <div class="cf-proof-pill tech"><span class="cf-proof-pill-icon">▸</span> $pill_4lang</div>
        <div class="cf-proof-pill prod"><span class="cf-proof-pill-icon">▸</span> $pill_9chap</div>
        <div class="cf-proof-pill prod"><span class="cf-proof-pill-icon">▸</span> $pill_modules</div>
        <div class="cf-proof-pill prod"><span class="cf-proof-pill-icon">▸</span> $pill_price</div>
        <div class="cf-proof-pill prod"><span class="cf-proof-pill-icon">▸</span> $pill_nomonthly</div>
      </section>

      <nav class="cf-pager" aria-label="$course_index">
        <a class="cf-btn cf-btn-ghost" href="$prev_url">
          <span>$prev</span>
          <b>$prev_num. $prev_title</b>
        </a>$next_block
      </nav>
    </main>

    <aside class="cf-sidecar" aria-label="$sidecar_live">
      <div class="cf-sidecar-label"><span class="dot"></span> $sidecar_live</div>
      <div class="cf-sidecar-tabs" role="tablist">
        <span class="cf-sidecar-tab active" role="tab" aria-selected="true">$sidecar_tab_exercise</span>
        <span class="cf-sidecar-tab" role="tab" aria-disabled="true">$sidecar_tab_history</span>
        <span class="cf-sidecar-tab" role="tab" aria-disabled="true">$sidecar_tab_hint</span>
      </div>
      <div class="cf-sidecar-hint">
        <b>$sidecar_task_title</b>
        $sidecar_hint_tail_a <a href="https://github.com/notifuturo/cyberfuturo/tree/main/curriculum/lessons/$slug" target="_blank" rel="noopener" style="color: var(--accent-2);">$sidecar_hint_tail_b</a>. $sidecar_hint_tail_c
      </div>
      <div class="cf-sidecar-actions">
        <a class="cf-btn cf-btn-tiny cf-btn-ghost" href="https://codespaces.new/notifuturo/cyberfuturo?quickstart=1" target="_blank" rel="noopener">$sidecar_open</a>
      </div>
    </aside>

  </div>

  <div class="cf-drawer" id="toc">
    <div class="cf-drawer-inner">
      <a class="cf-drawer-close" href="#">$drawer_close</a>
      <nav class="cf-toc" aria-label="$drawer_aria">
        <div class="cf-toc-title">$course_index</div>
        <div class="cf-toc-root">$course_root</div>
        <ul class="cf-toc-tree">$toc_items_short</ul>
        <div class="cf-toc-unlock">
          <div class="cf-toc-unlock-label">$unlock_heading</div>
          <div class="cf-toc-unlock-price">$banner_price <span>$unlock_price_note</span></div>
          <a class="cf-btn cf-btn-primary" href="$buy_path" style="width: 100%; justify-content: center;">$unlock_cta</a>
        </div>
      </nav>
    </div>
  </div>
</div>

<footer class="footer">
  <div><strong>CyberFuturo</strong> $footer_brand_tag</div>
  <div>
    <a href="/$lang/">$footer_home</a>
    &nbsp;·&nbsp; <a href="/$lang/$course_dir/">$footer_course</a>
    &nbsp;·&nbsp; <a href="$buy_path">$footer_buy</a>
    &nbsp;·&nbsp; <a href="$privacy_path">$footer_privacy</a>
  </div>
</footer>

<script>
  (function() {
    var lang = document.documentElement.lang.slice(0, 2).toLowerCase();
    if (!/^(pt|es|en|fr)$$/.test(lang)) return;
    document.cookie = "cf_lang=" + lang + "; path=/; max-age=15552000; SameSite=Lax";
    var sel = document.querySelector('.lang-switcher a[data-lang="' + lang + '"]');
    if (sel) sel.classList.add("active");
  })();
</script>

</body>
</html>
""")


PRIVACY_PATH = {
    "pt": "/pt/privacidade/", "es": "/es/privacidad/",
    "en": "/en/privacy/", "fr": "/fr/confidentialite/",
}


def build_toc(lang: str, current_n: int, short: bool = False) -> str:
    """Return the <li>...</li> HTML for the TOC tree."""
    lbl = LABELS[lang]
    course = COURSE_DIR[lang]
    out = []
    for i, ch in enumerate(CHAPTERS):
        is_last = (i == len(CHAPTERS) - 1)
        branch = "└── " if is_last else "├── "
        num = f"{ch['n']:02d}"
        title = ch["titles"][lang]
        # Mobile drawer gets shorter names.
        display_title = title.split(" ")[0] if short and ch["n"] > 0 else title
        if ch["n"] == current_n:
            out.append(
                f'<li class="current"><span><span class="cf-toc-branch">{branch}</span>'
                f'<span class="cf-toc-num">{num}</span>'
                f'<span class="cf-toc-name">{display_title}</span>'
                f'<span class="cf-toc-status current">{lbl["reading"]}</span></span></li>'
            )
        elif ch["state"] == "sample":
            out.append(
                f'<li><a href="/{lang}/{course}/{ch["slug"]}/">'
                f'<span class="cf-toc-branch">{branch}</span>'
                f'<span class="cf-toc-num">{num}</span>'
                f'<span class="cf-toc-name">{display_title}</span>'
                f'<span class="cf-toc-status read">{lbl["free_sample"]}</span></a></li>'
            )
        elif ch["state"] == "preview":
            out.append(
                f'<li><a href="/{lang}/{course}/{ch["slug"]}/">'
                f'<span class="cf-toc-branch">{branch}</span>'
                f'<span class="cf-toc-num">{num}</span>'
                f'<span class="cf-toc-name">{display_title}</span>'
                f'<span class="cf-toc-status">· {lbl["preview"]}</span></a></li>'
            )
        else:
            # Other locked chapters — link to the preview page (which is itself
            # this file for peers). Keeps navigation free between previews.
            out.append(
                f'<li class="locked"><a href="/{lang}/{course}/{ch["slug"]}/">'
                f'<span class="cf-toc-branch">{branch}</span>'
                f'<span class="cf-toc-num">{num}</span>'
                f'<span class="cf-toc-name">{display_title}</span>'
                f'<span class="cf-toc-status">🔒</span></a></li>'
            )
    return "".join(out)


def chapter_page_url(lang: str, slug: str) -> str:
    return f"https://cyberfuturo.com/{lang}/{COURSE_DIR[lang]}/{slug}/"


def render_chapter(n: int, lang: str) -> str:
    """Render one chapter preview page."""
    ch = next(c for c in CHAPTERS if c["n"] == n)
    lbl = LABELS[lang]
    content = PREVIEW[n][lang]
    course = COURSE_DIR[lang]

    # Neighbours.
    prev_ch = CHAPTERS[n - 1] if n > 0 else None
    next_ch = CHAPTERS[n + 1] if n < len(CHAPTERS) - 1 else None

    # "Next" button: accessible preview if chapter is free/preview/locked-preview,
    # or "UNLOCK NEXT" primary-cta if there is no next.
    if next_ch is not None:
        next_block = (
            f'\n        <a class="cf-btn cf-btn-primary next" href="/{lang}/{course}/{next_ch["slug"]}/">'
            f'\n          <span>{lbl["next"]}</span>'
            f'\n          <b>{next_ch["n"]:02d}. {next_ch["titles"][lang]}</b>'
            f"\n        </a>"
        )
    else:
        next_block = (
            f'\n        <a class="cf-btn cf-btn-primary next" href="{BUY_PATH[lang]}">'
            f'\n          <span>{lbl["next"]}</span>'
            f"\n          <b>—</b>"
            f"\n        </a>"
        )

    will_bullets = "\n            ".join(
        f"<li style='margin-bottom: 10px;'>{b}</li>" for b in content["will"]
    )
    cont_bullets = "\n              ".join(f"<li>{b}</li>" for b in content["cont"])

    # Progress: crude — (n / 9) * 100.
    progress = int((n / 9) * 100)

    # URL chains for hreflang.
    urls = {l: chapter_page_url(l, ch["slug"]) for l in LANGS}

    title = ch["titles"][lang]
    meta_desc = f"{title}. {content['lead'][:120]}"
    og_desc = f"{title}. {lbl['preview_eyebrow']} + {lbl['end_title'].lower()}."

    out = TPL.substitute(
        locale=LOCALE[lang],
        og_locale=OG_LOCALE[lang],
        lang=lang,
        course_dir=course,
        title=title,
        meta_desc=meta_desc.replace('"', '&quot;'),
        og_desc=og_desc.replace('"', '&quot;'),
        self_url=urls[lang],
        pt_url=urls["pt"],
        es_url=urls["es"],
        en_url=urls["en"],
        fr_url=urls["fr"],
        skip_text=lbl["skip"],
        toc_open=lbl["toc_open"],
        index_text=lbl["index"],
        course_index=lbl["course_index"],
        course_root=lbl["course_root"],
        preview_word=lbl["preview"],
        sidecar_select=lbl["sidecar_select"],
        buy_tiny=lbl["buy_tiny"],
        buy_path=BUY_PATH[lang],
        nn=f"{n:02d}",
        mins=ch["mins"],
        progress=progress,
        banner_line_a=lbl["banner_line_a"],
        banner_strong=lbl["banner_strong"],
        banner_line_b=lbl["banner_line_b"],
        banner_line_c=lbl["banner_line_c"],
        banner_price=lbl["banner_price"],
        banner_tail=lbl["banner_tail"],
        banner_cta=lbl["banner_cta"],
        unlock_heading=lbl["unlock_heading"],
        unlock_price_note=lbl["unlock_price_note"],
        unlock_cta=lbl["unlock_cta"],
        toc_items=build_toc(lang, n, short=False),
        toc_items_short=build_toc(lang, n, short=True),
        eye_num=lbl["eye_num"],
        eye_paid_preview=lbl["eye_paid_preview"],
        lead=content["lead"],
        preview_eyebrow=lbl["preview_eyebrow"],
        will_bullets=will_bullets,
        end_title=lbl["end_title"],
        end_lead=lbl["end_lead"],
        end_cta=lbl["end_cta"],
        cont_bullets=cont_bullets,
        prev_url=f"/{lang}/{course}/{prev_ch['slug']}/" if prev_ch else "#",
        prev=lbl["prev"],
        prev_num=f"{prev_ch['n']:02d}" if prev_ch else "—",
        prev_title=prev_ch["titles"][lang] if prev_ch else "",
        next_block=next_block,
        drawer_close=lbl["drawer_close"],
        drawer_aria=lbl["drawer_aria"],
        sidecar_live=lbl["sidecar_live"],
        sidecar_tab_exercise=lbl["sidecar_tab_exercise"],
        sidecar_tab_history=lbl["sidecar_tab_history"],
        sidecar_tab_hint=lbl["sidecar_tab_hint"],
        sidecar_open=lbl["sidecar_open"],
        sidecar_task_title=lbl["sidecar_task_title"],
        sidecar_hint_tail_a=lbl["sidecar_hint_tail_a"],
        sidecar_hint_tail_b=lbl["sidecar_hint_tail_b"],
        sidecar_hint_tail_c=lbl["sidecar_hint_tail_c"],
        slug=ch["slug"],
        pill_stdlib=lbl["pill_stdlib"],
        pill_nobuild=lbl["pill_nobuild"],
        pill_works=lbl["pill_works"],
        pill_4lang=lbl["pill_4lang"],
        pill_9chap=lbl["pill_9chap"],
        pill_modules=lbl["pill_modules"],
        pill_price=lbl["pill_price"],
        pill_nomonthly=lbl["pill_nomonthly"],
        footer_brand_tag=lbl["footer_brand_tag"],
        footer_home=lbl["footer_home"],
        footer_course=lbl["footer_course"],
        footer_buy=lbl["footer_buy"],
        footer_privacy=lbl["footer_privacy"],
        privacy_path=PRIVACY_PATH[lang],
    )
    return out


def main() -> int:
    root = Path(__file__).resolve().parent.parent / "site"
    written = 0
    for n in range(2, 9):
        for lang in LANGS:
            ch = next(c for c in CHAPTERS if c["n"] == n)
            out_dir = root / lang / COURSE_DIR[lang] / ch["slug"]
            out_dir.mkdir(parents=True, exist_ok=True)
            target = out_dir / "index.html"
            target.write_text(render_chapter(n, lang), encoding="utf-8")
            print(f"wrote {target.relative_to(root.parent)}")
            written += 1
    print(f"\n{written} chapter-preview pages written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
