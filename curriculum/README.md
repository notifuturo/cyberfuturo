# CyberFuturo — el curso

> **Aprende tecnología al revés.** GUI → Terminal → Git → SQL → Python.
> Todo en tu navegador, sin instalar nada.

Este directorio contiene el curso completo. Si estás leyendo esto dentro de un Codespace,
ya tienes todo lo necesario para empezar. Si llegaste aquí desde GitHub, haz clic en el
botón verde **Code → Open in Codespaces**.

## Empezar

```bash
cd curriculum
./cf start
```

Eso arranca la primera lección que no hayas completado todavía.

## Comandos del runner

| Comando | Qué hace |
|---|---|
| `./cf list` | Lista todas las lecciones con su estado |
| `./cf start [n]` | Empieza la lección `n` (o la siguiente sin completar) |
| `./cf show` | Re-imprime las instrucciones de la lección actual |
| `./cf check` | Valida la lección actual |
| `./cf next` | Avanza a la siguiente lección (después de pasar el check) |
| `./cf progress` | Muestra tu progreso global |
| `./cf reset` | Reinicia tu progreso |
| `./cf help` | Ayuda |

## Cómo están organizadas las lecciones

Cada lección vive en `lessons/NN-slug/` y contiene:

- `lesson.md` — las instrucciones que lees
- `test.py` — el validador automático de la lección

Tu progreso se guarda en `.progress.json` (este archivo está en `.gitignore` para que cada
estudiante tenga su propio progreso en su fork).

## Lecciones disponibles (v0.1)

| # | Nombre | Tiempo |
|---|---|---|
| 00 | Bienvenida — tu primer archivo | ~15 min |
| 01 | Navegar el sistema de archivos | ~25 min |
| 02 | Tu primer commit en Git | ~30 min |
| 03 | Tu primer script en Python | ~30 min |

Próximamente: SQL con SQLite, GitHub + branches, HTTP + APIs con curl.

## Filosofía

- **Las lecciones son tareas reales**, no quizzes ni multiple choice.
- **Los tests verifican el estado real** de tus archivos, tu repo Git, o la salida de tus
  programas — no comparan texto con una respuesta pre-escrita.
- **El runner es Python stdlib puro**, 0 dependencias. Si algo rompe, puedes leer el código
  tú mismo y arreglarlo.
- **Progreso = commits**. Cada lección completada es una nueva entrada en tu historial de
  Git. Al final del curso tienes un repo con 30+ commits reales para poner en tu CV.

## Si algo no funciona

1. Lee cuidadosamente el mensaje de error que te dio `./cf check`. Los tests tratan de
   darte una pista específica.
2. Corre `./cf show` para re-leer las instrucciones de la lección actual.
3. Revisa el archivo `test.py` de la lección actual — es Python legible, puedes ver
   exactamente qué está buscando.
4. Abre un issue en el repositorio de GitHub.

## Licencia

MIT sobre el código. CC-BY-4.0 sobre el contenido de las lecciones. Úsalo, modifícalo,
tradúcelo, enséñalo. Solo atribúyelo.
