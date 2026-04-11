# Tu primer commit en Git

Git es el sistema de control de versiones que usa el 95% del mundo del software. Hace una
cosa: guarda instantáneas de tu código a lo largo del tiempo. Cada instantánea se llama un
**commit**. Un commit tiene un mensaje corto que explica qué cambió. Todo tu trabajo
quedará registrado como una lista de commits que puedes ver con `git log`.

En esta lección vas a crear un mini-proyecto, inicializarlo como un repositorio Git, y
hacer tu primer commit real.

## Tu tarea

Dentro de `curriculum/` hay que crear un directorio llamado `mi-proyecto/` que contenga:

1. Un archivo `README.md` con exactamente esta línea: `# mi-proyecto`
2. Un archivo `notas.txt` con cualquier texto que quieras (lo que sea, de al menos 3 caracteres)
3. El directorio debe ser un repositorio Git con **al menos un commit** que incluya ambos
   archivos

## Comandos que vas a usar

```
mkdir mi-proyecto              ← crear el directorio
cd mi-proyecto                 ← entrar al directorio
echo "# mi-proyecto" > README.md
echo "hola" > notas.txt

git init                       ← inicializar un repositorio git aquí
git status                     ← ver qué archivos están y cuál es su estado
git add .                      ← agregar todos los archivos al "área de staging"
git commit -m "mensaje"        ← crear un commit con ese mensaje
git log                        ← ver la historia de commits
```

## Pistas

- Si nunca usaste Git, la primera vez puede pedirte un nombre y un correo. Si pasa eso,
  ejecuta:
  ```
  git config --global user.email "tu@correo.com"
  git config --global user.name "Tu Nombre"
  ```
- `git status` es el comando más importante. Úsalo **mucho**. Después de cada paso, para ver
  qué ve Git.
- Cuando hagas `git add .`, no pasa nada visible. Es normal. Git prepara los archivos para
  el commit, pero todavía no los guarda. `git status` te va a mostrar los archivos "staged".
- El mensaje de commit tiene que ser significativo. No pongas `"asdf"`. Pon algo como
  `"inicio del proyecto"` o `"primer commit"`. Un mensaje decente es parte de la tarea.

## Los pasos, uno por uno

1. `cd ~/curriculum`
2. `mkdir mi-proyecto && cd mi-proyecto`
3. `echo "# mi-proyecto" > README.md`
4. `echo "esta es mi primera nota" > notas.txt`
5. `git init`
6. `git status`  ← mira la salida. Los archivos aparecen en rojo, "untracked".
7. `git add .`
8. `git status`  ← ahora aparecen en verde, "Changes to be committed".
9. `git commit -m "inicio del proyecto"`
10. `git log`  ← vas a ver tu commit con un hash, tu nombre, y la fecha.
11. `cd ..` para volver a `curriculum/`, y después `./cf check`.

## Lo que acabas de aprender

- **git init** — convertir un directorio en un repositorio Git
- **git status** — ver qué cambió y qué está listo para commit
- **git add** — preparar archivos para ser commiteados
- **git commit -m "mensaje"** — crear una instantánea con un mensaje
- **git log** — ver la historia de commits
- Qué es "staging" (el área intermedia entre tu código y la historia)
