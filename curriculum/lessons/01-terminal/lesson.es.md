# Navegar el sistema de archivos

Ahora que ya sabes crear un archivo, vamos a aprender a movernos. Un sistema de archivos
es una estructura en forma de árbol: directorios dentro de directorios, con archivos en
las hojas. Los comandos para moverte y mirar son los que vas a usar **todos los días**
de tu carrera.

## Tu tarea

Dentro de `curriculum/lessons/01-terminal/workspace/` hay un directorio llamado
`laberinto/`. En alguna parte de ese laberinto hay un archivo oculto llamado `.premio`.
Tu tarea es **encontrarlo** y escribir su contenido en un archivo nuevo llamado `premio.txt`
en el directorio `curriculum/` (no en el workspace, en `curriculum/` directamente).

## Comandos que vas a usar

```
cd <ruta>          ← cambiar de directorio
cd ..              ← subir un nivel
cd                 ← volver al home
ls                 ← listar archivos
ls -a              ← listar TODOS los archivos (incluidos los ocultos: los que empiezan con .)
ls -la             ← lista larga con detalles
find . -name .premio  ← buscar un archivo por nombre desde aquí hacia abajo
cat <archivo>      ← leer el contenido
pwd                ← dónde estoy ahora
```

## Pistas

- Los archivos que empiezan con `.` son **archivos ocultos**. `ls` normal no los muestra;
  tienes que usar `ls -a`.
- El comando `find` es tu amigo. `find . -name .premio` va a buscar desde el directorio
  actual hacia abajo y va a imprimir la ruta del archivo si lo encuentra.
- Puedes usar `cat <ruta-completa>` para leer el archivo sin necesidad de hacer `cd` primero.
- Para escribir el contenido de un archivo en otro: `cat <origen> > <destino>`.

## Los pasos, uno por uno

1. `cd curriculum/lessons/01-terminal/workspace/laberinto`
2. Usa `ls -la` y `find` para explorar la estructura. Vas a ver algunos directorios anidados.
3. Encuentra `.premio` con `find . -name .premio`. El comando te da la ruta.
4. Léelo con `cat <ruta>`. Verifica el contenido.
5. Vuelve a `cd ~/curriculum` (o `cd` hasta llegar al directorio `curriculum/`).
6. Escribe el contenido en `premio.txt` con `cat <ruta-del-.premio> > premio.txt`.
7. Ejecuta `./cf check`.

## Lo que acabas de aprender

- **cd** — moverse entre directorios
- **ls -la** — ver archivos ocultos y detalles
- **find** — buscar archivos por nombre
- **cat origen > destino** — copiar contenido de un archivo a otro
- Qué son los archivos ocultos (los que empiezan con `.`)
