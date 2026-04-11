# Bienvenida — tu primer archivo

Estás en una máquina virtual, en un navegador. No instalaste nada. Eso que se ve abajo de esta
ventana con el cursor parpadeando es una **terminal**, y a partir de ahora es tu herramienta
principal.

La terminal es un programa que acepta comandos escritos y los ejecuta. Cada comando es una
palabra (a veces con argumentos). Al final del comando, presionas Enter, y el programa hace
algo y te devuelve el control.

## Tu tarea

Dentro del directorio actual hay un archivo que tú vas a crear. Se llama `hola.txt` y su
contenido es exactamente el texto **hola mundo** seguido de un salto de línea.

## Comandos que vas a necesitar

```
pwd                           ← imprime "print working directory"
ls                            ← lista los archivos del directorio actual
echo "hola mundo" > hola.txt  ← crea un archivo con el texto dado
cat hola.txt                  ← imprime el contenido del archivo
```

## Los pasos, uno por uno

1. Ejecuta `pwd`. Eso te muestra dónde estás en el sistema de archivos.
2. Ejecuta `ls`. Eso te muestra qué archivos hay aquí. No deberías ver `hola.txt` todavía.
3. Ejecuta `echo "hola mundo" > hola.txt`. El símbolo `>` redirige la salida del comando
   a un archivo. Estás creando `hola.txt` con ese contenido en una sola línea.
4. Ejecuta `cat hola.txt`. Debería imprimir `hola mundo` en pantalla.
5. Cuando estés listo, ejecuta `./cf check` para validar.

## Si algo sale mal

- Si el archivo queda con comillas dentro del texto, probablemente escribiste
  `echo hola mundo` sin las comillas o usaste comillas curvas. Borra el archivo con
  `rm hola.txt` e intenta de nuevo.
- Si el contenido termina sin salto de línea, el test te lo va a decir con un mensaje útil.
- Si te equivocaste de directorio, vuelve con `cd ~/curriculum` y verifica con `pwd`.

## Lo que acabas de aprender

- **pwd** — dónde estás
- **ls** — qué hay aquí
- **echo** — imprimir texto en pantalla (o redirigirlo a un archivo)
- **cat** — leer un archivo
- **>** — redirigir la salida a un archivo
