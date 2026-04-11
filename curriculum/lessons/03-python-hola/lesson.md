# Tu primer script en Python

Hasta ahora hemos usado el terminal para mover archivos y hacer commits. Ahora vas a escribir
tu primer programa — un script en Python — y a ejecutarlo desde la misma terminal que ya
sabes usar.

Un script de Python es solo un archivo de texto con extensión `.py` que contiene instrucciones
que el intérprete entiende. Se ejecuta con el comando `python3 nombre.py`.

## Tu tarea

Vas a crear un script que reciba un nombre como argumento y lo salude. Específicamente:

1. Crea un archivo `curriculum/saludo.py`
2. Cuando lo ejecutes como `python3 saludo.py Luis`, debe imprimir exactamente:
   ```
   Hola, Luis!
   ```
3. Cuando lo ejecutes sin argumentos (`python3 saludo.py`), debe imprimir:
   ```
   Hola, mundo!
   ```

Ese mismo script se puede ejecutar con cualquier nombre: `python3 saludo.py Ana` debe
imprimir `Hola, Ana!`.

## Conceptos que vas a necesitar

**Lectura de argumentos desde la línea de comandos** — Python tiene un módulo llamado `sys`
que te da acceso a los argumentos con los que se invocó el script:

```python
import sys
# sys.argv[0] es el nombre del script
# sys.argv[1], sys.argv[2]... son los argumentos que te pasaron
```

**Imprimir texto** — la función incorporada `print` imprime lo que le pases:

```python
print("Hola, mundo!")
```

**f-strings** — una forma moderna de insertar variables en cadenas:

```python
nombre = "Ana"
print(f"Hola, {nombre}!")
```

**Control de flujo** — ejecuta una rama u otra según una condición:

```python
if condicion:
    ...
else:
    ...
```

## Un ejemplo muy cercano

Fíjate que este no es exactamente lo que te pide la tarea, pero está muy cerca:

```python
import sys

print("esto siempre se imprime")
print(f"nombre del script: {sys.argv[0]}")
print(f"argumentos: {sys.argv[1:]}")
```

Adáptalo: lee `sys.argv[1:]`, si está vacío usa `"mundo"`, si no usa el primero, y construye
la cadena de salida con una f-string.

## Los pasos, uno por uno

1. `cd ~/curriculum`
2. Crea `saludo.py` con tu editor favorito. Puedes usar nano (`nano saludo.py`) o VS Code
   directamente en el panel de archivos de la izquierda.
3. Escribe las ~6 líneas de código.
4. Prueba: `python3 saludo.py` → debe imprimir `Hola, mundo!`
5. Prueba: `python3 saludo.py Ana` → debe imprimir `Hola, Ana!`
6. Cuando ambos casos funcionen, corre `./cf check`.

## Lo que acabas de aprender

- **python3 archivo.py** — ejecutar un script Python desde el terminal
- **sys.argv** — leer los argumentos de la línea de comandos
- **print()** — imprimir algo
- **f-strings** — formato moderno para interpolar variables en cadenas
- **if / else** — control de flujo básico
