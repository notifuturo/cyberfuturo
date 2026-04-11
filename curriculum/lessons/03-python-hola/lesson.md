# Seu primeiro script em Python

Até agora a gente usou o terminal pra mover arquivos e fazer commits. Agora você vai
escrever seu primeiro programa — um script em Python — e rodar ele pelo mesmo terminal
que você já sabe usar.

Um script Python é só um arquivo de texto com extensão `.py` que contém instruções que o
interpretador entende. Ele é executado com o comando `python3 nome.py`.

## Sua tarefa

Você vai criar um script que recebe um nome como argumento e cumprimenta. Especificamente:

1. Crie um arquivo `curriculum/saudacao.py`
2. Quando você rodar como `python3 saudacao.py Luiz`, ele precisa imprimir exatamente:
   ```
   Olá, Luiz!
   ```
3. Quando você rodar sem argumentos (`python3 saudacao.py`), ele precisa imprimir:
   ```
   Olá, mundo!
   ```

O mesmo script precisa funcionar com qualquer nome: `python3 saudacao.py Ana` deve
imprimir `Olá, Ana!`.

## Conceitos que você vai precisar

**Leitura de argumentos da linha de comando** — Python tem um módulo chamado `sys` que
te dá acesso aos argumentos com que o script foi chamado:

```python
import sys
# sys.argv[0] é o nome do script
# sys.argv[1], sys.argv[2]... são os argumentos que foram passados pra ele
```

**Imprimir texto** — a função embutida `print` imprime o que você passar:

```python
print("Olá, mundo!")
```

**f-strings** — uma forma moderna de inserir variáveis em strings:

```python
nome = "Ana"
print(f"Olá, {nome}!")
```

**Controle de fluxo** — executa um ramo ou outro conforme uma condição:

```python
if condicao:
    ...
else:
    ...
```

## Um exemplo bem próximo

Presta atenção que isso não é exatamente o que a tarefa pede, mas está bem perto:

```python
import sys

print("isso sempre é impresso")
print(f"nome do script: {sys.argv[0]}")
print(f"argumentos: {sys.argv[1:]}")
```

Adapte: leia `sys.argv[1:]`, se estiver vazio use `"mundo"`, se não use o primeiro, e
monte a string de saída com uma f-string.

## Os passos, um por um

1. `cd ~/curriculum`
2. Crie `saudacao.py` com seu editor favorito. Você pode usar nano (`nano saudacao.py`)
   ou VS Code direto no painel de arquivos à esquerda.
3. Escreva as ~6 linhas de código.
4. Teste: `python3 saudacao.py` → deve imprimir `Olá, mundo!`
5. Teste: `python3 saudacao.py Ana` → deve imprimir `Olá, Ana!`
6. Quando os dois casos funcionarem, rode `./cf check`.

## O que você acabou de aprender

- **python3 arquivo.py** — rodar um script Python pelo terminal
- **sys.argv** — ler os argumentos da linha de comando
- **print()** — imprimir alguma coisa
- **f-strings** — formato moderno para interpolar variáveis em strings
- **if / else** — controle de fluxo básico
